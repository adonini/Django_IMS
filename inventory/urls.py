from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name='index'),  # point the root path to index view
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),  # auth_views.LogoutView.as_view(template_name='inventory/logout.html'), name='logout'),
    path('items/<int:pk>/', views.Item_record.as_view(), name='item_record'),
    path('items/', views.Item_list.as_view(), name='item_list'),
    path('manage_item/', views.ManageItem.as_view(), name='manage-item'),
    path('manage_item/<int:pk>/', views.ManageItem.as_view(), name='manage-item-pk'),
    path('add_item/', views.AddItem.as_view(), name='add-item'),
    path('delete_item/', views.DeleteItem.as_view(), name='delete-item'),
    path('stock/', views.Stock.as_view(), name='stock'),
    path('stock/<int:pk>/', views.Stock_record.as_view(), name='stock-record'),
    path('manage_stock/<int:pid>/', views.ManageStock.as_view(), name='manage-stock'),
    path('manage_stock/<int:pid>/<int:pk>/', views.ManageStock.as_view(), name='manage-stock-pk'),
    path('add_stock/', views.AddStock.as_view(), name='add-stock'),
    path('purchases/', views.Purchases.as_view(), name='purchases'),
    path('manage_purchase/', views.ManagePurchase.as_view(), name='manage-purchase'),
    path('manage_purchase/<int:pk>/', views.ManagePurchase.as_view(), name='manage-purchase-pk'),
    path('add_purchase/', views.AddPurchase.as_view(), name='add-purchase')
]
