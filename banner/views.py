from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics
from .models import FastBanner, SecondBanner
from .serializers import FastBannerSerializer, SecondBannerSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def banners_root(request):
    return Response({
        "fast-banners": request.build_absolute_uri("fast-banners/"),
        "second-banners": request.build_absolute_uri("second-banners/"),
    })

# FastBanner Views
class FastBannerListCreateView(generics.ListCreateAPIView):
    queryset = FastBanner.objects.all()
    serializer_class = FastBannerSerializer

class FastBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FastBanner.objects.all()
    serializer_class = FastBannerSerializer

# SecondBanner Views
class SecondBannerListCreateView(generics.ListCreateAPIView):
    queryset = SecondBanner.objects.all()
    serializer_class = SecondBannerSerializer

class SecondBannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SecondBanner.objects.all()
    serializer_class = SecondBannerSerializer
