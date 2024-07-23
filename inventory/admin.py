from django.contrib import admin
from .models import StockItem, Item, Category, Producer, Location, Zone

admin.site.register(Category)
admin.site.register(Producer)
admin.site.register(Item)
admin.site.register(StockItem)
admin.site.register(Location)
admin.site.register(Zone)
