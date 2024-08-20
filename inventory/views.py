from django.shortcuts import render, redirect
#from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView
#from django.views.generic.detail import DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserRegisterForm, AddItemForm, AddStockForm, AddPurchaseForm, AddPurchaseGroupForm
from .models import Item, Category, Producer, Stock
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
#from django.shortcuts import get_object_or_404
#from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.http import HttpResponse
import json
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
            form.save()
            # authenticate and login
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])

            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('index')

        return render(request, 'inventory/signup.html', {'form': form})

class Index(TemplateView):
    template_name = 'inventory/index.html'

class Item_list(LoginRequiredMixin, View):
    def get(self, request):
        context['page_title'] = 'Item list'
        items = Item.objects.all()
        stocks = Stock.objects.all()
        context['items'] = items
        context['stocks'] = stocks
        return render(request, 'inventory/item_list.html', context)

class Item_record(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Item Detail'
        if pk is None:
            messages.error(request, "Item ID is not recognized")
            return redirect('item_list')
        else:
            item = Item.objects.get(id=pk)
            stocks = Stock.objects.filter(item=item).all()
            context['item'] = item
            context['stocks'] = stocks
            return render(request, 'inventory/item_record.html', context)

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
                NewItem = form.save()
                NewItem.user = currentUser
                NewItem.save()
                messages.success(request, 'Item has been saved successfully!')
                resp['status'] = 'success'
            else:
                for fields in form:
                    for error in fields.errors:
                        resp['msg'] += str(error + "<br>")
        else:
            resp['msg'] = 'No data has been sent.'
        return HttpResponse(json.dumps(resp), content_type='application/json')

class ManageItem(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = "Manage Item"
        if not pk is None:
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

class Stock_list(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Stock'
        print(pk)
        if pk is None:
            items = Item.objects.all()
            context['items'] = items
        else:
            item = Item.objects.get(id=pk)
            stocks = Stock.objects.filter(item=item).all()
            context['items'] = item
            context['stocks'] = stocks
        print(context)
        return render(request, 'inventory/stock.html', context)

class Stock_record(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        context['page_title'] = 'Stock Detail'
        if pk is None:
            messages.error(request, "Item ID is not recognized")
            return redirect('stock')
        else:
            item = Item.objects.get(id=pk)
            stocks = Stock.objects.filter(item=item).order_by('-date_created').all() #This orders the item stock movements from most recent to older
            context['item'] = item
            context['stocks'] = stocks
            return render(request, 'inventory/stock_record.html', context)

class AddStock(LoginRequiredMixin, View):
    def post(self, request):
        resp = {'status': 'failed', 'msg': ''}
        currentUser = User.objects.get(username=request.user)
        if request.method == 'POST':
            print('ciao')
            if (request.POST['id']).isnumeric():
                stock = Stock.objects.get(pk=request.POST['id'])
            else:
                stock = None
            print('stock: ', stock)
            if stock is None:
                form = AddStockForm(request.POST)
            else:
                form = AddStockForm(request.POST, instance=stock)
            if form.is_valid():
                NewStock = form.save()
                NewStock.user = currentUser
                NewStock.save()
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
    def get(self, request, pid=None, pk=None):
        print('pid: ', pid)
        if pid is None:
            messages.error(request, "Item ID is not recognized")
            return redirect('stock')
        print('pk: ', pk)
        context['pid'] = pid
        if pk is None:
            context['page_title'] = "Add New Stock"
            context['stock'] = {}
        else:
            context['page_title'] = "Manage New Stock"
            stock = Stock.objects.get(id=pk)
            context['stock'] = stock
        return render(request, 'inventory/manage_stock.html', context)
