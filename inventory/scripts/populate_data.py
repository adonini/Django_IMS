from django.db.models.signals import post_migrate
from django.dispatch import receiver
from ..models import Stock_Type, Item_status, Purchase_status, Location, Zone, Telescope, Unit, Payment_sources, Category, Sub_category, Group
from django.contrib.auth.models import Group as G, Permission

def run():

    ItemStatuses_entries = [
        {'name': 'Purchased'},
        {'name': 'Stored'},
        {'name': 'Broken'},
        {'name': 'Installed'},
    ]
    PurchaseStatuses_entries = [
        {'name': 'Purchased'},
        {'name': 'Received'},
        {'name': 'Returned'},
    ]
    StockTypes_entries = [
        {'name': 'Stock In'},
        {'name': 'Stock Out'},
    ]
    Location_zones_entries = [
        {0: {'name': 'Mirca'},
         1: [{'name': 'General'}]},
        {0: {'name': 'Commissioning container'},
         1: [{'name': 'C1S0'}, {'name': 'C1S1'}, {'name': 'C1S2'}, {'name': 'C1S3'}, {'name': 'C2S0'}, {'name': 'C2S1'}, {'name': 'C2S2'}, {'name': 'C2S3'}, {'name': 'C3S0'}, {'name': 'C3S1'}, {'name': 'C3S2'}, {'name': 'C3S3'}, {'name': 'C4S0'}, {'name': 'C4S1'}, {'name': 'C4S2'}, {'name': 'C4S3'}]},
        {0: {'name': 'IT container'},
         1: [{'name': 'General'}]},
        {0: {'name': 'Storage container'},
         1: [{'name': 'General'}]},
        {0: {'name': 'Calp'},
         1: [{'name': 'General'}]},
    ]
    Unit_entries = [
        {
            "name": "Centimeter",
            "short_name": "cm"
        },
        {
            "name": "Meter",
            "short_name": "m"
        },
        {
            "name": "Millimeter",
            "short_name": "mm"
        },
        {
            "name": "Inch",
            "short_name": "in"
        },
        {
            "name": "Foot",
            "short_name": "ft"
        },
        {
            "name": "Square Meter",
            "short_name": "m²"
        },
        {
            "name": "Square Foot",
            "short_name": "ft²"
        },
        {
            "name": "Cubic Meter",
            "short_name": "m³"
        },
        {
            "name": "Cubic Foot",
            "short_name": "ft³"
        },
        {
            "name": "Liter",
            "short_name": "L"
        },
        {
            "name": "Gallon",
            "short_name": "gal"
        },
        {
            "name": "Kilogram",
            "short_name": "kg"
        },
        {
            "name": "Gram",
            "short_name": "g"
        },
        {
            "name": "Pound",
            "short_name": "lb"
        },
        {
            "name": "Ounce",
            "short_name": "oz"
        },
        {
            "name": "Unit",
            "short_name": "unit"
        }
    ]

    Telescope_entries = [
        {"name": "LST1"},
        {"name": "LST2"},
        {"name": "LST3"},
        {"name": "LST4"},
    ]

    Payment_entries = [
        {"name": "Common Found"} #Need to incude all
    ]
    Categories_sub_groups_entries = [ #Not finished, just an example
        {0: {"name": "Mount",
             "PBS_code": "8.1.1"},
         1: [{0: {"name": "Lower structure",
                  "PBS_code": "8.1.1.1"},
              1: [{"name": "Central Pin Bearing",
                   "PBS_code": "8.1.1.10.1"},
                  {"name": "Central pin shaft encoder",
                   "PBS_code": "8.1.1.10.2"},
                  {"name": "Central Pin Radial shaft Seal",
                   "PBS_code": "8.1.1.10.3"},
                  {"name": "Heavy bogie's Motor",
                   "PBS_code": "8.1.1.8.1 "},
                  {"name": "Motor's encoder",
                   "PBS_code": "8.1.1.8.2 "},
                  {"name": "Heavy bogie motor's Gearbox",
                   "PBS_code": "8.1.1.8.3"},
                  {"name": "Heavy bogie",
                   "PBS_code": "8.1.1.8.4"},
                  {"name": "Heavy bogie's pinion",
                   "PBS_code": "8.1.1.8.7"},
                  {"name": "Heavy bogie's guiding wheels",
                   "PBS_code": "8.1.1.8.8"},
                  {"name": "Heavy bogie's anti up-lifting wheels",
                   "PBS_code": "8.1.1.8.9"},
                  {"name": "Heavy bogie's Broom & dry lubrication scrapers",
                   "PBS_code": "8.1.1.8.10"},
                  {"name": "Heavy bogie's linear guides",
                   "PBS_code": "8.1.1.8.11"},
                  {"name": "Heavy bogie's spherical joint",
                   "PBS_code": "8.1.1.8.12"},
                  {"name": "Light bogie",
                   "PBS_code": "8.1.1.8.13"},
                  {"name": "Light bogie's guiding wheels",
                   "PBS_code": "8.1.1.8.17"},
                  {"name": "Light bogie's anti up-lifting wheels",
                   "PBS_code": "8.1.1.8.18"},
                  {"name": "Light bogie's Broom & dry lubrication scrapers",
                   "PBS_code": "8.1.1.8.19"},
                  {"name": "Light bogie's linear guides",
                   "PBS_code": "8.1.1.8.20"},
                  {"name": "Light bogie's spherical joint",
                   "PBS_code": "8.1.1.8.21"},
                  ]},
                  {0: {"name": "Elevation Drive",
                       "PBS_code": "8.1.1.2"},
                   1: [{"name": "Drive Gear Bearing",
                        "PBS_code": "8.1.1.2.1"},
                        {"name": "Hand Wheel Bearing",
                        "PBS_code": "8.1.1.2.2"},
                        {"name": "Radial Guiding Wheels",
                        "PBS_code": "8.1.1.2.3"},
                        {"name": "Lateral Guiding Wheels",
                        "PBS_code": "8.1.1.2.4"},
                        {"name": "Chain",
                        "PBS_code": "8.1.1.2.5"},
                        {"name": "Drive gear",
                        "PBS_code": "8.1.1.2.6"},
                        {"name": "Brake",
                        "PBS_code": "8.1.1.2.7"},
                        {"name": "Elevation Drive Inductive Sensor",
                        "PBS_code": "8.1.1.2.8"},
                        {"name": "Motor",
                        "PBS_code": "8.1.1.2.9"},
                        {"name": "Elevation Motor's encoder",
                        "PBS_code": "8.1.1.2.10"},
                        {"name": "Planetary gearbox",
                        "PBS_code": "8.1.1.2.11"},
                        {"name": "Inclinometer",
                        "PBS_code": "8.1.1.2.12"},
                        {"name": "Clutch",
                        "PBS_code": "8.1.1.2.13"},
                        {"name": "Handwheel gearbox",
                        "PBS_code": "8.1.1.2.14"},
                        {"name": "Handwheel clutch",
                        "PBS_code": "8.1.1.2.15"},
                        ]}, 
                        {0: {"name": "Elevation Bearing",
                             "PBS_code": "8.1.1.3"},
                         1: [{"name": "Elevation bearing",
                              "PBS_code": "8.1.1.3.1"},
                              {"name": "Shaft encoder Elevation",
                               "PBS_code": "8.1.1.3.2"},
                              ]}]}
    ]

    admin_groups_entries = [
        {"name": "admin"},
        {"name": "technician"},
        {"name": "user"},
    ]

    print("Adding data into DB...")

    if not Stock_Type.objects.exists():
        for entry in StockTypes_entries:
            Stock_Type.objects.get_or_create(**entry)
    else:
        print("There was data on stock types.")

    if not Item_status.objects.exists():
        for entry in ItemStatuses_entries:
            Item_status.objects.get_or_create(**entry)
    else:
        print("There was data on item status.")

    if not Purchase_status.objects.exists():
        for entry in PurchaseStatuses_entries:
            Purchase_status.objects.get_or_create(**entry)
    else:
        print("There was data on purchase status.")
    
    if not Location.objects.exists() and not Zone.objects.exists():
        for entry in  Location_zones_entries:
            location, success = Location.objects.get_or_create(**entry[0])
            for zone in entry[1]:
                zone['location'] = location
                Zone.objects.get_or_create(**zone)
    else:
        print("There was data on location or zone.")

    if not Telescope.objects.exists():
        for entry in Telescope_entries:
            Telescope.objects.get_or_create(**entry)
    else:
        print("There was data on telescope.")

    if not Unit.objects.exists():
        for entry in Unit_entries:
            Unit.objects.get_or_create(**entry)
    else:
        print("There was data on unit.")

    if not Payment_sources.objects.exists():
        for entry in Payment_entries:
            Payment_sources.objects.get_or_create(**entry)
    else:
        print("There was data on payment source.")
        
    if not Category.objects.exists() and not Sub_category.objects.exists() and not Group.objects.exists():
        for entry in Categories_sub_groups_entries:
            category, success = Category.objects.get_or_create(**entry[0])
            for sub in entry[1]:
                sub[0]["category"] = category
                sub_category, success = Sub_category.objects.get_or_create(**sub[0])
                for group in sub[1]:
                    group["sub_category"] = sub_category
                    Group.objects.get_or_create(**group)
    else:
        print("There was data on category, sub-category or group.")

    if not G.objects.exists():
        for index, entry in enumerate(admin_groups_entries):
            group, success = G.objects.get_or_create(**entry)
            if index == 0:
                all_permission = Permission.objects.all()
                group.permissions.set(all_permission)
            elif index == 1:
                view_permissions = Permission.objects.filter(codename__startswith='view_')
                other_permissions = Permission.objects.filter(codename__in=["add_item", "change_item", "add_stock", "change_stock"])
                group.permissions.set(view_permissions)
                group.permissions.add(*other_permissions)
            else:
                view_permissions = Permission.objects.filter(codename__startswith='view_')
                group.permissions.set(view_permissions)

    else:
        print("There was data on auth group.")

    print("Done!")
