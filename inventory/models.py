from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.dispatch import receiver


class Item(models.Model):
    code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='-')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    producer = models.ForeignKey('Producer', on_delete=models.SET_NULL, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    serials = models.CharField(max_length=100, validators=[validate_comma_separated_integer_list], blank=True, null=True,
                               default='', help_text="Enter serial numbers as a comma-separated list of integers.")
    #serials = models.TextField(blank=True, null=True, help_text='If more items, add serial numbers separated by a comma.')
    #quantity = models.IntegerField()
    #price = models.FloatField(default=0)
    #status = models.CharField(max_length=2, choices=(('1','Active'),('2','Inactive')), default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'items'

    def __str__(self):
        return self.code + ' - ' + self.name  # join code and name

    def split_serials(self):
        if self.serials:
            # Remove any leading or trailing whitespace and split the serials string
            serial_numbers = [serial.strip() for serial in self.serials.split(',') if serial.strip()]
            #print(','.join(serial_numbers))
            return ','.join(serial_numbers)
        return ''

    def count_inventory(self):
        stocks = StockItem.objects.filter(item=self)
        stockIn = 0
        stockOut = 0
        for stock in stocks:
            if stock.type.id == 1:
                stockIn = int(stockIn) + int(stock.quantity)
            else:
                stockOut = int(stockOut) + int(stock.quantity)
        available = stockIn - stockOut
        return available
    


# class ItemSerialNumber(models.Model):
#     serial_number = models.CharField(max_length=100)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.serial_number

class StockOPTypes(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'stock_op_types'

    def __str__(self):
        return self.name
    
class StockItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)  #on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    reorder_point = models.IntegerField(default=0)
    area = models.ForeignKey('Location', on_delete=models.SET_NULL, blank=True, null=True)
    shelf = models.ForeignKey('Zone', on_delete=models.SET_NULL, blank=True, null=True)
    #broken_units = models.IntegerField(default=0)
    type = models.ForeignKey(StockOPTypes, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'stock_items'

    def __str__(self):
        if self.item:
            return self.item.code + ' - ' + self.item.name
        else:
            return "No associated item"


class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
        
class Producer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'producers'

    def __str__(self):
        return self.name
    

class Purchase(models.Model):
    order_number = models.CharField(max_length=200)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(default=date_created)
    quantity = models.FloatField(default=0)
    price_per_item = models.FloatField(default=0)
    tracking_url = models.CharField(max_length=255, blank=True, null=True)
    received = models.BooleanField(default=0)
    creator_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_purchases')
    receiver_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='received_purchases')

    class Meta:
        db_table = 'purchases'

    def __str__(self):
        return self.order_number
    
    def calculateAmount(self):
        return float(self.quantity) * float(self.price_per_item)

class Purchase(models.Model):
    order_number = models.CharField(max_length=200)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(default=date_created)
    quantity = models.FloatField(default=0)
    price_per_item = models.FloatField(default=0)
    tracking_url = models.CharField(max_length=255, blank=True, null=True)
    received = models.BooleanField(default=0)
    creator_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_purchases')
    receiver_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='received_purchases')

    class Meta:
        db_table = 'purchases'

    def __str__(self):
        return self.order_number
    
    def calculateAmount(self):
        return float(self.quantity) * float(self.price_per_item)
        
class Location(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        db_table = 'locations'

    def __str__(self):
        return self.name
    
class Zone(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    class Meta:
        db_table = 'zones'

    def __str__(self):
        return self.name



# @receiver(models.signals.post_save, sender=Invoice_Item)
# def stock_update(sender, instance, **kwargs):
#     stock = StockItem(product=instance.product, quantity = instance.quantity, type = 2)
#     stock.save()
#     # stockID = Stock.objects.last().id
#     Invoice_Item.objects.filter(id= instance.id).update(stock=stock)