from django.contrib import admin
from .models import StockItem, Item, Category

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(StockItem)
