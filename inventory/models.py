from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    PBS_code = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'

class Sub_category(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    PBS_code = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sub-categories'

class Unit(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'units'

class Group(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    PBS_code = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    sub_category = models.ForeignKey(Sub_category, on_delete=models.CASCADE, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='imgs/', blank=True, null=True)
    minimum_stock = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups'

class Producer(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'producers'

class Telescope(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    image = models.ImageField(upload_to='imgs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telescopes'

class Item_status(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items_statuses'

class Item(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=150, blank=True, null=True)
    serial_number = models.CharField(max_length=150, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    producer = models.ForeignKey(Producer, on_delete=models.SET_NULL, null=True)
    price = models.FloatField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    datasheet_url = models.CharField(max_length=100, blank=True, null=True)
    status = models.ForeignKey(Item_status, on_delete=models.SET_NULL, null=True)
    telescope = models.ForeignKey(Telescope, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items'

    def __str__(self):
        return self.code + ' - ' + self.name  # join code and name

    def count_inventory(self):
        stocks = Stock.objects.filter(item=self)
        stockIn = 0
        stockOut = 0
        for elements in stocks:
            if elements.type.id == 1:
                stockIn = int(stockIn) + int(elements.quantity)
            else:
                stockOut = int(stockOut) + int(elements.quantity)
        available = stockIn - stockOut
        return available
    
class Stock_Type(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_types'

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'locations'

class Zone(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'zones'    
    
class Stock(models.Model):
    zone= models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    stock_type = models.ForeignKey(Stock_Type, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        db_table = 'stocks'

    def __str__(self):
        if self.item:
            return self.item.code + ' - ' + self.item.name
        else:
            return "No associated item"

class Payment_sources(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_sources'

class Purchase_status(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_statuses'

class Purchase_group(models.Model):
    order_number = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.FloatField(blank=True, null=True)
    status = models.ForeignKey(Purchase_status, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment_sources, on_delete=models.SET_NULL, null=True)
    creator_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="creator")
    receiver_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="receiver")
    standard_lead_time = models.IntegerField(default=7)
    expected_delivery_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_groups'

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suppliers'

class Purchase(models.Model):
    price_per_item = models.FloatField(blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    purchase_group = models.ForeignKey(Purchase_group, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchases'

# @receiver(models.signals.post_save, sender=Invoice_Item)
# def stock_update(sender, instance, **kwargs):
#     stock = StockItem(product=instance.product, quantity = instance.quantity, type = 2)
#     stock.save()
#     # stockID = Stock.objects.last().id
#     Invoice_Item.objects.filter(id= instance.id).update(stock=stock)