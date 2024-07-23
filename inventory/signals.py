from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import StockOPTypes, Location, Zone
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_default_entries(sender, **kwargs):
    if sender.name == 'inventory':  # app name
        # default values
        StockTypes_entries = [
            {'name': 'Stock In'},
            {'name': 'Stock Out'},
        ]
        Location_entries = [
            {'name': 'Mirca'},
            {'name': 'Commissioning container'},
            {'name': 'IT container'},
            {'name': 'Storage container'},
            {'name': 'CALP'},
        ]
        Zone_entries = [
            {'name' : 'Default'}
        ]

        for entry in StockTypes_entries:
            StockOPTypes.objects.get_or_create(**entry)

        for entry in Location_entries:
            location = Location.objects.get_or_create(**entry)
            for zone in Zone_entries:
                zone['name'] = location[0].name+" "+zone['name']
                zone['location'] = location[0]
                Zone.objects.get_or_create(**zone)
                zone['name'] = zone['name'].replace(location[0].name+" ", "")
            #Here we can create zones for each location, we can either create the same zones for all of them or specifically create zones for each location getting the value of the entry name