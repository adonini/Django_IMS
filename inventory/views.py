from django.shortcuts import render, redirect
#from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView
#from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group as G
from .forms import UserRegisterForm, AddItemForm, AddStockForm, AddPurchaseForm, AddPurchaseGroupForm, ModifyStockForm
from .models import Item, Category, Producer, Stock, Sub_category, Group, Telescope, Item_status, Location, Zone, Stock_Type, Purchase_status, Purchase_group, Purchase, Payment_sources, Supplier, Telescope_structure, PartNumber
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
#from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse
import json
from django.core.serializers import serialize
from django.db import IntegrityError
from django.db.models import Q
from django.db import connection
from datetime import date, timedelta
from django.utils import timezone
from django.forms.models import model_to_dict
import re
import logging

logger = logging.getLogger(__name__)

context = {
    'page_title': 'File Management System',
}

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('index')

class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'inventory/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            try: 
                group = G.objects.get(name='user')
            except G.DoesNotExist:
                group = G.objects.create(name='user')
            if isinstance(group, G):
                user.groups.add(group)
            # authenticate and login
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])

            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('index')

        return render(request, 'inventory/signup.html', {'form': form})

class Index(View):
    def get(self, request):
        context['page_title'] = 'Dashboard'
        groups = PartNumber.objects.all()
        critical_stock = []
        low_stock = []
        for index, group in enumerate(groups):
            if group.minimum_stock and (group.group_stock() - group.minimum_stock) <= 2:
                stock = group.group_stock()
                group = model_to_dict(group, fields=['id', 'name', 'minimum_stock'])
                group['group_stock'] = stock
                if len(critical_stock) < 3:
                    critical_stock.append(group)
            elif group.minimum_stock and (group.group_stock() - group.minimum_stock) <= 4 and (group.group_stock() - group.minimum_stock) > 2:
                stock = group.group_stock()
                group = model_to_dict(group, fields=['id', 'name', 'minimum_stock'])
                group['group_stock'] = stock
                if len(low_stock) < 3:
                    low_stock.append(group)
        today = timezone.now().date()
        query1 = '''
            SELECT id, table_name, column_name, row_id, old_value, new_value, changed_at, changed_by
            FROM public.history_modifications 
            where column_name = 'status_id' and new_value = '5' order by changed_at desc limit 5;
        '''
        query2='''
            SELECT id, table_name, column_name, row_id, old_value, new_value, changed_at, changed_by
            FROM public.history_modifications
            where row_id in (SELECT related_id from public.audit_log where operation_type = 'DELETE' and table_name = 'stocks' order by performed_at desc limit 5) and column_name = 'telescope_id';
        '''
        query3='''
            SELECT id, item_id, status_id, group_id, part_number, serial_number, deleted_by, deleted_at
            FROM public.deleted_items
            where item_id = %s;
        '''
        latestUsed = []
        with connection.cursor() as cursor:
            cursor.execute(query1)
            results = cursor.fetchall()
            if results:
                for result in results:
                    item = Item.objects.filter(pk=result[3]).exclude(status=Item_status.objects.get(name='Broken'))
                    if item:
                        item = item[0]
                        if item.part_number:
                            latestUsed.append({'itemName': item.part_number.group.name, 'itempart_number':item.part_number, 'date': result[6], 'user': result[7], 'telescope': item.telescope})
                        elif item.serial_number:
                            latestUsed.append({'itemName': item.part_number.group.name, 'itemSerial':item.serial_number, 'date': result[6], 'user': result[7], 'telescope': item.telescope})
                        else:
                            latestUsed.append({'itemName': item.part_number.group.name, 'itemPk': item.pk, 'date': result[6], 'user': result[7], 'telescope': item.telescope.telescope.name+" - "+item.telescope.name})
        context['latest_used'] = latestUsed
        context['next_purchases'] = Purchase_group.objects.exclude(status=Purchase_status.objects.get(name='Received')).order_by('expected_delivery_date').filter(expected_delivery_date__gte=today)[:5]
        purchasesIds = list(Purchase_group.objects.exclude(status=Purchase_status.objects.get(name='Received')).order_by('expected_delivery_date').filter(expected_delivery_date__gte=today).values_list('id', flat=True)[:5])
        context['purchases_related'] = list(Purchase.objects.filter(purchase_group_id__in=purchasesIds).values('purchase_group_id', 'item_id'))
        context['critical_stock'] = critical_stock
        context['low_stock'] = low_stock
        context['items_data'] =  list(Item.objects.values('id', 'part_number__group__name', 'part_number__code', 'serial_number'))
        return render(request, 'inventory/index.html', context)

class Item_list(LoginRequiredMixin, View):
    def get(self, request):
        items = Item.objects.order_by('part_number')
        item_list = list(items.values('part_number__group', 'part_number', 'serial_number', 'model', 'producer', 'price', 'expiration_date', 'datasheet_url', 'status', 'telescope'))
        for item in item_list:
            item['expiration_date'] = str(item['expiration_date'])
        item_json = json.dumps(item_list)
        context['page_title'] = 'Item list'
        context['items'] = items
        context['item_data'] = item_json
        context['categories'] =  list(Category.objects.order_by('name').values('id', 'name'))
        context['subCategories'] =  list(Sub_category.objects.order_by('name').values('id', 'name', 'category'))
        context['groups'] =  list(Group.objects.order_by('name').values('id', 'name', 'sub_category'))
        context['producers'] =  list(Producer.objects.order_by('name').values('id', 'name'))
        context['telescopes'] =  list(Telescope.objects.order_by('name').values('id', 'name'))
        context['telescope_structures'] =  list(Telescope_structure.objects.order_by('name').values('id', 'name', 'telescope__name'))
        context['statuses'] = list(Item_status.objects.order_by('name').values('id', 'name'))
        context['zones'] = Zone.objects.order_by('location__name').all()
        user = request.user
        context['userGroups'] = list(user.groups.values_list('name', flat=True))
        return render(request, 'inventory/item_list.html', context)

class Item_record(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Item Information'
        if pk is None:
            messages.error(request, "Item ID is not recognized")
            return redirect('item_list')
        else:
            item = Item.objects.get(id=pk)
            stocks = Stock.objects.filter(item=item).all()
            if item.status:
                if item.status.name == 'In use':
                    with connection.cursor() as cursor:
                        status = Item_status.objects.get(name='In use')
                        cursor.execute("SELECT * FROM history_modifications WHERE column_name = 'status_id' AND row_id = %s AND new_value = %s", [str(item.pk), str(status.pk)])
                        rows = cursor.fetchall()
                        context['instalation_date'] = rows[0][6]
            context['item'] = item
            context['stocks'] = stocks
            return render(request, 'inventory/item_record.html', context)
        
class Producer_record(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Producer Information'
        if pk is None:
            messages.error(request, "Producer ID is not recognized")
            return redirect('item_list')
        else:
            producer = Producer.objects.get(id=pk)
            print(producer)
            context['producer'] = producer
            return render(request, 'inventory/producer_record.html', context)

class AddItem(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        currentUser = User.objects.get(username=request.user)
        if request.method == 'POST':
            if (request.POST['id']).isnumeric():
                item = Item.objects.get(pk=request.POST['id'])
            else:
                item = None
            if item is None:
                form = AddItemForm(request.POST)
            else:
                form = AddItemForm(request.POST, instance=item)
            if form.is_valid():
                if 'quantity' in request.POST:
                    for i in range(1, int(request.POST['quantity'])+1):
                        newItem = form.save(commit=False)
                        newItem.user = currentUser
                        newItem.pk = None
                        newItem.save()
                    messages.success(request, 'Item has been saved successfully!')
                else:
                    newItem = form.save()
                    messages.success(request, 'Item has been saved successfully!')
                resp['status'] = 'success'
            else:
                for fields in form:
                    for error in fields.errors:
                        if fields.name == 'part_number':
                            resp['msg'] += str(f'Part Number: {error}' + "<br>")
                        else:
                            resp['msg'] += str(f'{fields.label}: {error}' + "<br>")
        else:
            resp['msg'] = 'No data has been sent.'
        return HttpResponse(json.dumps(resp), content_type='application/json')

class ManageItem(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = "Manage Item"
        context['today'] = date.today()
        partNumber_data = {}
        groups = Group.objects.all()
        for group in groups:
            partNumbers = list(PartNumber.objects.filter(group=group).values('id', 'code', 'group'))
            if partNumbers:
                partNumber_data[group.id] = partNumbers
        context['partNumber_data'] = json.dumps(partNumber_data)
        if pk:
            item = Item.objects.get(id=pk)
            context['item'] = item
        else:
            context['item'] = {}
            context['categories'] = Category.objects.all()
            context['producers'] = Producer.objects.all()
        return render(request, 'inventory/manage_item.html', context)

class DeleteItem(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            try:
                item = Item.objects.get(id=request.POST['id'])
                item.delete()
                messages.success(request, 'Item has been deleted successfully!')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Item has failed to delete!'
                print(err)
        else:
            resp['msg'] = 'Item has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")

class BrokenItem(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            try:
                currentUser = User.objects.get(username=request.user)
                item = Item.objects.get(id=request.POST['id'])
                if item.status != Item_status.objects.get(name='Stored'):
                    newStock = Stock(
                        zone = Zone.objects.get(pk=request.POST['zone']),
                        stock_type = Stock_Type.objects.get(pk=1),
                        item = item,
                        quantity = 1,
                        user = currentUser,
                    )
                    newStock.save()
                else:
                    foundStock = Stock.objects.get(item=item)
                    foundStock.zone = Zone.objects.get(pk=request.POST['zone'])
                    foundStock.save()
                item.status = Item_status.objects.get(name='Broken')
                if item.telescope:
                    item.telescope = None
                item.save()
                messages.success(request, 'Item now is broken.')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Item has failed to delete!'
                print(err)
        else:
            resp['msg'] = 'Item has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    def get(self, request, pk=None):
        context['page_title'] = "Broken Item"
        context['zones'] = Zone.objects.all()
        if pk:
            item = Item.objects.get(pk=pk)
            context['item'] = item
            if item.status == Item_status.objects.get(name= 'Stored'):
                context['stock'] = Stock.objects.get(item=item)
        return render(request, 'inventory/broken.html', context)

class FixItem(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            try:
                item = Item.objects.get(id=request.POST['id'])
                item.status = Item_status.objects.get(name='Stored')
                item.save()
                messages.success(request, 'Item has been fixed! Now you can use it on the Stock tab.')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Item has failed to delete!'
                print(err)
        else:
            resp['msg'] = 'Item has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
class ModifyItemStatus(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        resp = {'status': 'failed', 'msg': ''}
        if request.POST:
            item = Item.objects.get(pk=pk)
            if request.POST['zone'][0] != '0':
                logger.debug(Zone.objects.get(pk=request.POST['zone'][0]))
            if request.POST['broken']:
                item.status = Item_status.objects.get(name='Broken')
                item.save()
            messages.success(request, 'There is information!')
            resp['status'] = 'success'
        return HttpResponse(json.dumps(resp), content_type="application/json")

class Stock_list(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context = {}
        context['page_title'] = 'Stock'
        source = request.GET.get('source', '')
        if source:
            context['source'] = source
        if pk is None:
            items = Item.objects.all()
            stocks = Stock.objects.order_by('item', 'zone').distinct('item', 'zone')
            context['items'] = items
            context['stocks'] = stocks
            context['groups'] =  list(Group.objects.order_by('name').values('id', 'name'))
            context['producers'] =  list(Producer.objects.order_by('name').values('id', 'name'))
            context['zones'] =  list(Zone.objects.order_by('location__name').values('id', 'name', 'location'))
            context['locations'] =  list(Location.objects.order_by('name').values('id', 'name'))
            numbers = PartNumber.objects.all()
            context['allGroups'] = []
            for number in numbers:
                if number.minimum_stock:
                    result = number.group_stock()-number.minimum_stock
                    if result < 2:
                        result = 'Critical'
                    elif result <= 4:
                        result = 'Low'
                    else:
                        result = 'Ok'
                    group_data = {
                        'group': number,
                        'part_number': number.code,
                        'stock': number.group_stock(),
                        'purchase': number.pending_purchases(number.code),
                        'status': result
                    }
                    context['allGroups'].append(group_data)
        return render(request, 'inventory/stock.html', context)

class Stock_record(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Stock Detail'
        if pk is None:
            messages.error(request, "Item ID is not recognized")
            return redirect('stock')
        else:
            stock = list(Stock.objects.filter(id=pk)) #.order_by('-created_at').all() #This orders the item stock movements from most recent to older this might be get not filter
            stock_entries = list(Stock.objects.filter(item=stock[0].item, zone=stock[0].zone).order_by('-created_at'))
            context['stock'] = stock[0]
            context['stock_entries'] = stock_entries
            return render(request, 'inventory/stock_record.html', context)

class AddStock(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        currentUser = User.objects.get(username=request.user)
        if request.method == 'POST':
            if (request.POST['id']).isnumeric():
                stock = Stock.objects.get(pk=request.POST['id'])
            else:
                stock = None
            if stock is None:
                form = AddStockForm(request.POST)
            else:
                form = ModifyStockForm(request.POST, instance=stock)
            if form.is_valid():
                if request.POST['id'] and not 'telescope' in request.POST:
                    form.save()
                    messages.success(request, 'Stock has been moved successfully.')
                elif 'telescope' in request.POST and request.POST['stock_type'] == "2":
                    item = Stock.objects.get(pk=request.POST['id']).item
                    if request.POST['telescope'] == "None":
                        item.status = Item_status.objects.get(name='In use')
                        item.save()
                    else:
                        telescope = Telescope_structure.objects.get(id=int(request.POST['telescope']))
                        item.status = Item_status.objects.get(name='In use')
                        item.telescope = telescope
                        item.save()
                        stock_entry = Stock.objects.get(pk=request.POST['id'])
                        stock_entry.delete()
                    messages.success(request, 'Item usage saved successfully.')
                else:
                    NewStock = form.save()
                    NewStock.user = currentUser
                    NewStock.save()
                    item = Item.objects.get(pk=request.POST['item'])
                    storedStatus = Item_status.objects.get(name='Stored')
                    item.status = storedStatus
                            
                    if request.POST['part_number'] is not None:
                        item.part_number = request.POST['part_number']
                    if request.POST['serial_number'] is not None:
                        item.serial_number = request.POST['serial_number']
                    item.save()
                    messages.success(request, 'Stock has been saved successfully.')
                resp['status'] = 'success'
            else:
                for fields in form:
                    for error in fields.errors:
                        resp['msg'] += str(error + "<br>")
        else:
            print('bye bye')
            resp['msg'] = 'No data has been sent.'
        return HttpResponse(json.dumps(resp), content_type='application/json')

class ManageStock(LoginRequiredMixin, View):
    def get(self, request, operation=None, pk=None):
        if pk is None:
            if operation == 'add':
                storedStatus = Item_status.objects.get(name='Purchased').id
                items = Item.objects.filter(Q(status_id=storedStatus) | Q(status__isnull=True)).order_by('group__name')
                unStockedItems = list(Item.objects.filter(status_id=None).values('id', 'group', 'part_number', 'serial_number'))
                context['items'] = items
                context['unStockedItems'] = unStockedItems
                context['operation'] = 1
            zones = Zone.objects.order_by('location__name').all()
            context['zones'] = zones
            types = Stock_Type.objects.all()
            context['types'] = types
            context['stock_data'] =  list(Stock.objects.values('id', 'zone', 'item'))    
            context['page_title'] = "Add New Stock"
            context['stock'] = {}
        else:
            if operation == 'use':
                stock = Stock.objects.get(id=pk)
                telescopes = Telescope_structure.objects.all()
                zones = Zone.objects.order_by('location__name').all()
                context['zones'] = zones
                types = Stock_Type.objects.all()
                context['types'] = types
                context['stock'] = stock
                context['telescopes'] = telescopes
                context['operation'] = 2
            else:
                context['page_title'] = "Manage Stock"
                stock = Stock.objects.get(id=pk)
                zones = Zone.objects.order_by('location__name').all()
                context['stock'] = stock
                context['zones'] = zones
                context['operation'] = 'move'
                return render(request, 'inventory/move_stock.html', context)
        return render(request, 'inventory/manage_stock.html', context)

class MarkStockOld(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        stock = Stock.objects.get(pk = request.POST['id'])
        if stock:
            stock.old = True
            stock.save()
            resp['msg'] = 'Stock has been marked as old.'
            resp['status'] = 'success'
        return HttpResponse(json.dumps(resp), content_type='application/json')

class DeleteStock(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            try:
                stock = Stock.objects.get(id=request.POST['id'])
                stock.item.status = Item_status.objects.get(name='Unmanaged')
                stock.item.save()
                stock.delete()
                messages.success(request, 'Stock has been deleted successfully!')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Stock has failed to delete!'
                print(err)
        else:
            resp['msg'] = 'Stock has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")

class MoveMoreStock(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            data = request.POST
            data = data.dict()
            zoneFound = None
            for element in data:
                if element == 'zone':
                    zoneFound = Zone.objects.get(pk = data[element])
                else:
                    stockFound = Stock.objects.get(pk=data[element])
                    stockFound.zone = zoneFound
                    stockFound.save()
            messages.success(request, 'Stock has been moved successfully!')
            resp['status'] = 'success'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    def get(self, request):
        items = Item.objects.all()
        stocks = Stock.objects.order_by('item', 'zone').distinct('item', 'zone')
        zones = Zone.objects.order_by('location__name')
        context['items'] = items
        context['stocks'] = stocks
        context['groups'] =  list(Group.objects.order_by('name').values('id', 'name'))
        context['producers'] =  list(Producer.objects.order_by('name').values('id', 'name'))
        context['zones'] = zones
        context['zones_detail'] =  list(Zone.objects.order_by('location__name').values('id', 'name', 'location'))
        context['locations_detail'] =  list(Location.objects.order_by('name').values('id', 'name'))
        context['mode'] = 'move'
        return render(request, 'inventory/move_use_stock.html', context)
    
class UseMoreStock(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            data = request.POST
            data = data.dict()
            zoneFound = None
            for element in data:
                if element == 'place':
                    zoneFound = Telescope_structure.objects.get(pk = data[element])
                else:
                    stockFound = Stock.objects.get(pk=data[element])
                    stockFound.item.telescope = zoneFound
                    stockFound.item.status = Item_status.objects.get(name='In use')
                    stockFound.item.save()
                    stockFound.delete()
            messages.success(request, 'Stock has been moved successfully!')
            resp['status'] = 'success'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    def get(self, request):
        items = Item.objects.all()
        stocks = Stock.objects.order_by('item', 'zone').distinct('item', 'zone')
        telescopes = Telescope_structure.objects.order_by('telescope__name')
        context['items'] = items
        context['stocks'] = stocks
        context['groups'] =  list(Group.objects.order_by('name').values('id', 'name'))
        context['producers'] =  list(Producer.objects.order_by('name').values('id', 'name'))
        context['telescopes'] = telescopes
        context['mode'] = 'use'
        return render(request, 'inventory/move_use_stock.html', context)

class Purchase_list(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Purchases'
        if pk is None:
            source = request.GET.get('source', '')
            if source == 'dash':
                context['source'] = True
            else:
                if 'source' in context:
                    del context['source']
            items = Item.objects.all()
            purchases = Purchase_group.objects.all().order_by('-created_at')
            purchases_data = {}
            for purchase in purchases:
                purchases_data[purchase.id] = list(Purchase.objects.filter(purchase_group=purchase.id).values('item_id'))
            context['items'] = items
            context['purchases'] = purchases
            context['purchases_data'] =purchases_data
            context['statuses'] =  list(Purchase_status.objects.values('id', 'name'))
            context['items_data'] =  list(Item.objects.values('id', 'part_number__group__name', 'part_number__code', 'serial_number'))
        return render(request, 'inventory/purchases.html', context)
    
class ManagePurchase(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = "Manage Purchase"
        context['today'] = date.today()
        context['items'] = list(Item.objects.filter(status__isnull=True).values('id', 'part_number__group__name', 'part_number__code', 'serial_number'))
        context['payments'] = Payment_sources.objects.all()
        context['suppliers'] = Supplier.objects.all()
        if pk is not None: 
            context['foundPurchase'] = Purchase_group.objects.get(pk=pk)
        else:
            context['today'] = timezone.now()
            if 'foundPurchase' in context:
                context.pop('foundPurchase', None)
        return render(request, 'inventory/manage_purchase.html', context)

    
class ManagePurchaseSearch(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = "Manage Purchase Search"
        context['items'] = Item.objects.filter(status=Item_status.objects.get(name='Unmanaged'))
        context['item_prices'] = list(Item.objects.exclude(price=None).values('id', 'price'))
        return render(request, 'inventory/manage_purchase_search.html', context)
    
class Purchase_record(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Purchase Information'
        if pk is None:
            messages.error(request, "Purchase group ID is not recognized")
            return redirect('purchases')
        else:
            purchase_group = Purchase_group.objects.get(pk=pk)
            purchases = Purchase.objects.filter(purchase_group__id=purchase_group.pk)
            context['purchase_group'] = purchase_group
            context['purchases'] = purchases
            return render(request, 'inventory/purchase_record.html', context)

class AddPurchase(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        currentUser = User.objects.get(username=request.user)
        if request.method == 'POST':
            if (request.POST['id']).isnumeric():
                purchase = Purchase_group.objects.get(pk=request.POST['id'])
            else:
                purchase = None
            if purchase is None:
                form = AddPurchaseGroupForm(request.POST)
            else:
                form = AddPurchaseGroupForm(request.POST, instance=purchase)
            if form.is_valid():
                purchasedStatus = Purchase_status.objects.get(name='Purchased')
                newForm = form.save(commit=False)
                newForm.status = purchasedStatus
                newForm.creator_user = currentUser
                if not newForm.standard_lead_time:
                    newForm.standard_lead_time = Purchase_group._meta.get_field('standard_lead_time').default
                if not newForm.expected_delivery_date:
                    newForm.expected_delivery_date = date.today() + timedelta(days=newForm.standard_lead_time)
                newForm.save()
                itemPattern = re.compile(r'^data\[\d+\]\[item\]$')
                pricePattern = re.compile(r'^data\[\d+\]\[price\]$')
                filtered_items = {key: value for key, value in request.POST.items() if itemPattern.match(key)}
                filtered_price = {key: value for key, value in request.POST.items() if pricePattern.match(key)}
                filtered_items = list(filtered_items.values())
                filtered_price = list(filtered_price.values())
                if len(filtered_items) == len(filtered_price):
                    for i in range(0, len(filtered_price)):
                        item = Item.objects.get(pk=filtered_items[i])
                        purchase = Purchase(
                            price_per_item = filtered_price[i],
                            item = item,
                            purchase_group = newForm
                        )
                        item.status = Item_status.objects.get(name='Purchased')
                        item.price = purchase.price_per_item
                        item.save()
                        purchase.save()
                messages.success(request, 'Purchase has been saved successfully!')
                resp['status'] = 'success'
            else:
                for fields in form:
                    field_name = fields.label
                    for error in fields.errors:
                        resp['msg'] += str(field_name+": "+error + "<br>")
        else:
            resp['msg'] = 'No data has been sent.'
        return HttpResponse(json.dumps(resp), content_type='application/json') 

class DeletePurchase(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}

        if request.method == 'POST':
            try:
                purchase = Purchase.objects.get(id=request.POST['id'])
                purchase.item.status = Item_status.objects.get(name='Unmanaged')
                purchase.item.save()
                purchase.delete()
                messages.success(request, 'Item has been deleted successfully from the purchase!')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Item has failed to delete!'
                print(err)
        else:
            resp['msg'] = 'Item has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
class DeletePurchaseGroup(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        if request.method == 'POST':
            try:
                purchaseGroup = Purchase_group.objects.get(id=request.POST['id'])
                purchases = Purchase.objects.filter(purchase_group = purchaseGroup)
                for purchase in purchases:
                    purchase.item.status = Item_status.objects.get(name='Unmanaged')
                    purchase.item.save()
                    purchase.delete()
                purchaseGroup.delete()
                messages.success(request, 'Purchase has been deleted successfully!')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Purchase has failed to delete!'
                print(err)
        else:
            resp['msg'] = 'Purchase has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")

class ReceivePurchase(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}

        if request.method == 'POST':
            try:
                body = json.loads(request.body)
                currentUser = User.objects.get(username=request.user)
                purchaseGroup = Purchase_group.objects.get(id=body['id'], status__name='Purchased')
                purchases = Purchase.objects.filter(purchase_group = purchaseGroup)
                purchaseGroup.status = Purchase_status.objects.get(name='Received')
                purchaseGroup.delivery_date = date.today()
                purchaseGroup.receiver_user = currentUser
                for purchase in purchases:
                    purchase.item.status = Item_status.objects.get(name='Stored')
                    purchase.item.serial_number = body['item_data'][str(purchase.item.pk)]['serial_number']
                    newStock = Stock(
                        zone = Zone.objects.get(pk=body['item_data'][str(purchase.item.pk)]['zone']),
                        stock_type = Stock_Type.objects.get(pk=1),
                        item = purchase.item,
                        quantity = 1,
                        user = currentUser,
                    )
                    newStock.save()
                    purchase.item.save()
                purchaseGroup.save()
                messages.success(request, 'Purchase has been received successfully!')
                resp['status'] = 'success'
            except Exception as err:
                resp['msg'] = 'Purchase has failed to delete!'
                logger.error(err)
        else:
            resp['msg'] = 'Purchase has failed to delete'
        return HttpResponse(json.dumps(resp), content_type="application/json")

class StorePurchase(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = "Store Purchase"
        if pk is not None:
            context['purchase'] = Purchase.objects.get(item__pk=pk)
        context['items'] = list(Item.objects.filter(status__isnull=True).values('id', 'part_number__group__name'))
        context['zones'] = Zone.objects.order_by('location__name').all()
        context['operation'] = 1
        return render(request, 'inventory/store-purchase.html', context)
#Not used
class removePurchasedStatus(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        logger.debug(request.POST)
        return HttpResponse(json.dumps(resp), content_type="application/json")
