from django.urls import path
from . import views
from .views import request_password_reset, reset_password

urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('orders/', views.orders, name='accounts.orders'),
    path('password_reset/', request_password_reset, name='password_reset'),
    path('reset_password/<str:token>/', reset_password, name='reset_password'),
]




