from django.urls import path
from .views import (
    banners_root,
    FastBannerListCreateView, FastBannerDetailView,
    SecondBannerListCreateView, SecondBannerDetailView
)

urlpatterns = [
    path("", banners_root, name="banners-root"),
    path("fast-banners/", FastBannerListCreateView.as_view(), name="fast-banner-list"),
    path("fast-banners/<int:pk>/", FastBannerDetailView.as_view(), name="fast-banner-detail"),
    path("second-banners/", SecondBannerListCreateView.as_view(), name="second-banner-list"),
    path("second-banners/<int:pk>/", SecondBannerDetailView.as_view(), name="second-banner-detail"),
]
