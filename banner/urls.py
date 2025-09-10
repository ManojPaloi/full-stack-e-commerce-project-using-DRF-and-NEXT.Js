from django.urls import path
from .views import (
    banners_root,
    FirstBannerListCreateView, FirstBannerDetailView,
    SecondBannerListCreateView, SecondBannerDetailView
)

urlpatterns = [
    path("", banners_root, name="banners-root"),
    path("first-banners/", FirstBannerListCreateView.as_view(), name="first-banner-list"),
    path("first-banners/<int:pk>/", FirstBannerDetailView.as_view(), name="first-banner-detail"),
    path("second-banners/", SecondBannerListCreateView.as_view(), name="second-banner-list"),
    path("second-banners/<int:pk>/", SecondBannerDetailView.as_view(), name="second-banner-detail"),
]
