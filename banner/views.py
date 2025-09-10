from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics
from .models import FirstBanner, SecondBanner
from .serializers import FirstBannerSerializer, SecondBannerSerializer

# Banners API root → shows sub-URLs
@api_view(['GET'])
@permission_classes([AllowAny])
def banners_root(request):
    return Response({
        "first-banners": request.build_absolute_uri("first-banners/"),
        "second-banners": request.build_absolute_uri("second-banners/"),
    })

# FirstBanner views
class FirstBannerListCreateView(generics.ListCreateAPIView):
    queryset = FirstBanner.objects.all()
    serializer_class = FirstBannerSerializer

class FirstBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FirstBanner.objects.all()
    serializer_class = FirstBannerSerializer

# SecondBanner views
class SecondBannerListCreateView(generics.ListCreateAPIView):
    queryset = SecondBanner.objects.all()
    serializer_class = SecondBannerSerializer

class SecondBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SecondBanner.objects.all()
    serializer_class = SecondBannerSerializer
