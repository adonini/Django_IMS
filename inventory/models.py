from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist


class Category(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    PBS_code = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Sub_category(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    PBS_code = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sub-categories'
        verbose_name = 'Sub-category'
        verbose_name_plural = 'Sub-categories'

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'units'

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    PBS_code = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    sub_category = models.ForeignKey(Sub_category, on_delete=models.CASCADE, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='imgs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups'

    def __str__(self):
        return self.name

class PartNumber(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=150, blank=False, null=False)
    minimum_stock = models.SmallIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'part_number'
        verbose_name = 'Part Number'
        verbose_name_plural = 'Part Numbers'

    def __str__(self):
        return f'{self.code}'
    
    def group_stock(self):
        stock_items = Stock.objects.filter(item__part_number=self.pk).exclude(item__status=Item_status.objects.get(name='Broken'))
        current_stock = len(stock_items)
        return current_stock

    def pending_purchases(self):
        purchase_items = Purchase.objects.filter(item__part_number=self.pk, purchase_group__status=Purchase_status.objects.get(name='Purchased'))
        current_purchase = len(purchase_items)
        return current_purchase

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

    def __str__(self):
        return self.name


class Telescope(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='-', null=True)
    image = models.ImageField(upload_to='imgs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telescopes'

    def __str__(self):
        return self.name


class Telescope_structure(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    telescope = models.ForeignKey(Telescope, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telescope_structures'

    def __str__(self):
        return self.name


class Item_status(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items_statuses'
        verbose_name = 'Item Status'
        verbose_name_plural = 'Item Statuses'

    def __str__(self):
        return self.name


def get_unmanaged_status():
    try:
        return Item_status.objects.get(name='Unmanaged')
    except ObjectDoesNotExist:
        return None


class Item(models.Model):
    part_number = models.ForeignKey(PartNumber, on_delete=models.CASCADE, null=True)
    serial_number = models.CharField(max_length=150, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    producer = models.ForeignKey(Producer, on_delete=models.SET_NULL, null=True)
    price = models.FloatField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    datasheet_url = models.CharField(max_length=100, blank=True, null=True)
    status = models.ForeignKey(Item_status, on_delete=models.SET_NULL, null=True, default=get_unmanaged_status)
    telescope = models.ForeignKey(Telescope_structure, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_stockObject(self):
        return Stock.objects.filter(item=self).first()

    class Meta:
        db_table = 'items'

    def __str__(self):
        return f'{self.part_number.group} - {self.model} ({self.serial_number})'


class Stock_Type(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_types'
        verbose_name = 'Stock Type'
        verbose_name_plural = 'Stock Types'

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'locations'

    def __str__(self):
        return self.name


class Zone(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'zones'

    def __str__(self):
        return self.name


class Stock(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    stock_type = models.ForeignKey(Stock_Type, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    old = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stocks'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stock'

    def __str__(self):
        return f'{self.item} - #{self.quantity}'

    def count_inventory(self):
        stocks = Stock.objects.filter(item__part_number__group__id=self.item.part_number.group.id, zone=self.zone)
        stockIn = 0
        stockOut = 0
        for elements in stocks:
            if elements.stock_type.id == 1:
                stockIn += int(elements.quantity)
            else:
                stockOut += int(elements.quantity)
        available = stockIn - stockOut
        return available


class Payment_sources(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_sources'
        verbose_name = 'Payment Source'
        verbose_name_plural = 'Payment Sources'

    def __str__(self):
        return self.name


class Purchase_status(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_statuses'
        verbose_name = 'Purchase Status'
        verbose_name_plural = 'Purchase Statuses'

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class Purchase_group(models.Model):
    order_number = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.CharField(max_length=100, blank=True, null=True)
    shipping_cost = models.FloatField(blank=True, null=True)
    status = models.ForeignKey(Purchase_status, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment_sources, on_delete=models.SET_NULL, null=True)
    creator_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="creator")
    receiver_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="receiver")
    standard_lead_time = models.IntegerField(default=7, null=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchase_groups'
        verbose_name = 'Purchase Group'
        verbose_name_plural = 'Purchase Groups'

    def calculate_amount(self):
        purchases = Purchase.objects.filter(purchase_group_id=self.pk)
        amount = 0
        for purchase in purchases:
            amount += purchase.price_per_item
        return amount

    def items_purchased(self):
        purchases = Purchase.objects.filter(purchase_group_id=self.pk)
        return len(purchases)

    def __str__(self):
        return f'# {self.order_number if self.order_number else "Unknown Order Number"}'


class Purchase(models.Model):
    price_per_item = models.FloatField(blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1, null=True)
    purchase_group = models.ForeignKey(Purchase_group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchases'

    def __str__(self):
        return f'Purchase {self.purchase_group} - {self.item} - {self.quantity} units'

# @receiver(models.signals.post_save, sender=Invoice_Item)
# def stock_update(sender, instance, **kwargs):
#     stock = StockItem(product=instance.product, quantity = instance.quantity, type = 2)
#     stock.save()
#     # stockID = Stock.objects.last().id
#     Invoice_Item.objects.filter(id= instance.id).update(stock=stock)
