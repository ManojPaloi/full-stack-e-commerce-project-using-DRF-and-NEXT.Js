from rest_framework import serializers
from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price", "subtotal"]
        read_only_fields = ["subtotal"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "method", "amount", "paid_at", "transaction_id"]
        read_only_fields = ["paid_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # remove read_only
    payment = PaymentSerializer(read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "customer", "full_name", "address", "city", "pin_code", "phone",
            "status", "total_price", "coupon", "discount_amount", "final_price",
            "created_at", "updated_at", "items", "payment",
        ]
        read_only_fields = ["status", "discount_amount", "final_price", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        
        # Assign logged-in user as customer
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["customer"] = request.user

        # Create the order
        order = Order.objects.create(**validated_data)

        # Create all OrderItems
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        # Apply coupon & save final price
        order.apply_coupon()
        order.save()

        return order


