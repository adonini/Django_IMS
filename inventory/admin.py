from django.contrib import admin
from .models import StockItem, Item, Category, Producer

admin.site.register(Category)
admin.site.register(Producer)
admin.site.register(Item)
admin.site.register(StockItem)
