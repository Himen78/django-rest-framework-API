from django.urls import path
from django.conf import settings
from .views import CreatedView, UpdateView, LoginUser, LogoutUser, UserGetView

urlpatterns = [
    path('api/register/', CreatedView.as_view(), name='register'),
    path('api/update/<int:id>/', UpdateView.as_view(), name='Update User'),
    path('api/get/<int:id>/', UserGetView.as_view(), name='Get User'),
    path('api/login/', LoginUser.as_view(), name='Login'),
    path('api/logout/', LogoutUser.as_view(), name='Logout')
]