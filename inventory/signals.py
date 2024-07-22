from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import StockOPTypes

@receiver(post_migrate)
def create_default_entries(sender, **kwargs):
    if sender.name == 'inventory':  # app name
        # default values
        StockTypes_entries = [
            {'name': 'Stock In'},
            {'name': 'Stock Out'},
        ]

        for entry in StockTypes_entries:
            StockOPTypes.objects.get_or_create(**entry)