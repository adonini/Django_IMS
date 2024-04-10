from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list


class Item(models.Model):
    code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(default='-')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
    producer = models.CharField(max_length=50, blank=True, null=True)
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

    def __str__(self):
        return self.code + ' - ' + self.name  # join code and name

    def split_serials(self):
        if self.serials:
            return self.serials.split(',')
        return []

    def count_inventory(self):
        stocks = StockItem.objects.filter(item=self)
        stockIn = 0
        stockOut = 0
        for stock in stocks:
            if stock.type == '1':
                stockIn = int(stockIn) + int(stock.quantity)
            else:
                stockOut = int(stockOut) + int(stock.quantity)
        available = stockIn - stockOut
        return available

class StockItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)  #on_delete=models.CASCADE)
    #category = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.FloatField(default=0)
    area = models.CharField(max_length=100, blank=True, null=True)
    shelf = models.CharField(max_length=100, blank=True, null=True)
    broken_units = models.IntegerField(default=0)
    type = models.CharField(max_length=2, choices=(('1', 'Stock-in'), ('2', 'Stock-Out')), default=1)

    #price = models.FloatField(default=0)
    #status = models.CharField(max_length=2, choices=(('1','Active'),('2','Inactive')), default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        if self.item:
            return self.item.code + ' - ' + self.item.name
        else:
            return "No associated item"


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
