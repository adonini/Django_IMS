from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name='index'),  # point the root path to index view
    path('stock/', views.Stock.as_view(), name='stock'),
    #path('add-item/', views.AddItem.as_view(), name='add-item'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),  # auth_views.LogoutView.as_view(template_name='inventory/logout.html'), name='logout'),
    path('items/<int:pk>/', views.Item_record.as_view(), name='item_record'),
    path('stock/<int:pk>/', views.Stock_record.as_view(), name='stock_record'),
    path('items/', views.Item_list.as_view(), name='item_list'),
]
