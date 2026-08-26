from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BoxViewSet, ProductViewSet, RecommendBoxView

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("boxes", BoxViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("recommend-box/", RecommendBoxView.as_view(), name="recommend-box"),
]
