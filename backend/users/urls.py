from django.urls import path
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('users/subscriptions/', UserViewSet.as_view({'get': 'subscriptions'})),
    path('users/<int:id>/subscribe/', UserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'})),
] + router.urls