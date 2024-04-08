from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, CreateView
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, InventoryItemForm
from .models import InventoryItem, Category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('index')


class Index(TemplateView):
    template_name = 'inventory/index.html'


class Stock(LoginRequiredMixin, View):
    def get(self, request):
        items = InventoryItem.objects.order_by('id')
        return render(request, 'inventory/stock.html', {'items': items})


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


class AddItem(LoginRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('stock')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
