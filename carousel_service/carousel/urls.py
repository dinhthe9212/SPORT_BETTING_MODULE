from rest_framework.routers import DefaultRouter
from .views import FeaturedEventViewSet

router = DefaultRouter()
router.register(r'carousel', FeaturedEventViewSet)

urlpatterns = router.urls


