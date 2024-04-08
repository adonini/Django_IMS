from django.contrib import admin
from django.urls import path
from .views import Index, SignUpView, Stock, AddItem
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', Index.as_view(), name='index'),  # point the root path to index view
    path('stock/', Stock.as_view(), name='stock'),
    path('add-item/', AddItem.as_view(), name='add-item'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),  # auth_views.LogoutView.as_view(template_name='inventory/logout.html'), name='logout'),
]
