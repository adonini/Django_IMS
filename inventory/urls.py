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
    path('producers/<int:pk>/', views.Producer_record.as_view(), name='producer_record'),
    path('manage_item/', views.ManageItem.as_view(), name='manage-item'),
    path('manage_item/<int:pk>/', views.ManageItem.as_view(), name='manage-item-pk'),
    path('add_item/', views.AddItem.as_view(), name='add-item'),
    path('delete_item/', views.DeleteItem.as_view(), name='delete-item'),
    path('modify_item_status/<int:pk>/', views.ModifyItemStatus.as_view(), name='modify-item-status'),
    path('stock/', views.Stock_list.as_view(), name='stock'),
    path('stock/<int:pk>/', views.Stock_record.as_view(), name='stock-record'),
    path('mark_stock_old/', views.MarkStockOld.as_view(), name='mark-stock-old'),
    path('delete_stock/', views.DeleteStock.as_view(), name='delete-stock'),
    path('manage_stock/', views.ManageStock.as_view(), name='manage-stock'),
    path('manage_stock/<int:pk>/', views.ManageStock.as_view(), name='manage-stock-pk'),
    path('manage_stock/Move', views.MoveMoreStock.as_view(), name='Movemore'),
    path('manage_stock/Use', views.UseMoreStock.as_view(), name='Usemore'),
    path('manage_stock/<str:operation>', views.ManageStock.as_view(), name='manage-stock'),
    path('manage_stock/<str:operation>/<int:pk>', views.ManageStock.as_view(), name='manage-stock-status-pk'),
    path('add_stock/', views.AddStock.as_view(), name='add-stock'),
    path('broken/', views.BrokenItem.as_view(), name='broken'),
    path('broken/<int:pk>', views.BrokenItem.as_view(), name='broken'),
    path('fix_item', views.FixItem.as_view(), name='fix-item'),
    path('purchases/', views.Purchase_list.as_view(), name='purchases'),
    path('purchases/<int:pk>/', views.Purchase_record.as_view(), name='purchase-record'),
    path('manage_purchase/', views.ManagePurchase.as_view(), name='manage-purchase'),
    path('manage_purchase/<int:pk>/', views.ManagePurchase.as_view(), name='manage-purchase'),
    path('manage_purchase_search/', views.ManagePurchaseSearch.as_view(), name='manage-purchase-search'),
    path('add_purchase/', views.AddPurchase.as_view(), name='add-purchase'),
    path('delete_purchase/', views.DeletePurchase.as_view(), name='delete-purchase'),
    path('delete_purchase_group/', views.DeletePurchaseGroup.as_view(), name='delete-purchase-group'),
    path('receive_purchase/', views.ReceivePurchase.as_view(), name='receive-purchase'),
    path('store_purchase/<int:pk>', views.StorePurchase.as_view(), name='store-purchase'),
    path('remove_status', views.removePurchasedStatus.as_view(), name='remove-status'),
]
