from django.urls import include, path
from rest_framework import routers
from .views import UserViewSet, check_if_friends, friends_list, delete_friend, \
manipulate_friend_request, friend_requests_list, create_friend_request
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('check_if_friends/<int:user_1>/<int:user_2>/', check_if_friends, name='check_if_friends  '),
    path('friend_list/<int:user_id>/', friends_list, name='friends_list'),
    path('delete_friend/<int:user_1>/<int:user_2>/', delete_friend, name='delete_friend'),
    path('manipulate_friend_request/<int:request_id>/', manipulate_friend_request, name='manipulate_friend_request'),
    path('create_friend_request/', create_friend_request, name='create_friend_request'),
    path('friend_requests_list/<int:user_id>/', friend_requests_list, name='friend_requests_list'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),


]