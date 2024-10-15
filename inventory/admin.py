from django.contrib import admin
from .models import Item, Category, Producer, Stock, Stock_Type, Sub_category, Supplier, Telescope, Unit, Group, Item_status, Location, Zone, Payment_sources, Purchase, Purchase_group, Purchase_status, PartNumber, Telescope_structure

admin.site.site_title = "LST IMS AP"
admin.site.site_header = "LST IMS Admin Panel"
admin.site.index_title = "Content manager"

admin.site.register(Producer)
admin.site.register(Stock)
admin.site.register(Stock_Type)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Sub_category)
admin.site.register(Telescope)
admin.site.register(Supplier)
admin.site.register(Unit)
admin.site.register(Group)
admin.site.register(Item_status)
admin.site.register(Location)
admin.site.register(Zone)
admin.site.register(Payment_sources)
admin.site.register(Purchase_status)
admin.site.register(Purchase_group)
admin.site.register(Purchase)
admin.site.register(PartNumber)
admin.site.register(Telescope_structure)
