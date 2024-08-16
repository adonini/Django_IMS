from django.contrib import admin
from .models import Stock, Item, Producer

admin.site.register(Producer)
admin.site.register(Item)
admin.site.register(Stock)
