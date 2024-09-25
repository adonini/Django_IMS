from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Category, Stock, Producer, Stock_Type, Group, Item_status, Telescope, Zone, Purchase_status, Purchase_group, Purchase, Payment_sources, Supplier


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AddItemForm(forms.ModelForm):
    producer = forms.ModelChoiceField(queryset=Producer.objects.all(), initial=0, required=False)  # to give the choice between already existing categories
    group = forms.ModelChoiceField(queryset=Group.objects.all(), initial=0, required=False)
    status = forms.ModelChoiceField(queryset=Item_status.objects.all(), initial=0, required=False)
    telescope = forms.ModelChoiceField(queryset=Telescope.objects.all(), initial=0, required=False)

    class Meta:
        model = Item
        fields = ['group', 'code', 'serial_number', 'price', 'producer', 'expiration_date', 'datasheet_url', 'status', 'telescope']

    # Here the code looks for an existing code same as the one inserted - celan_{field} is a django system to execute extra validations on some fields.
    def clean_code(self):
        id = self.instance.id if self.instance.id else 0
        code = self.cleaned_data['code']
        try:
            if int(id) > 0:
                item = Item.objects.exclude(id=id).get(code=code)
            else:
                item = Item.objects.get(code=code)
        except:
            return code
        raise forms.ValidationError(f"{code} Category Already Exists.")
    
    def clean_serial_number(self):
        id = self.instance.id if self.instance.id else 0
        serial_number = self.cleaned_data['serial_number']
        try:
            if int(id) > 0:
                item = Item.objects.exclude(id=id).get(serial_number=serial_number)
            else:
                item = Item.objects.get(serial_number=serial_number)
        except:
            return serial_number
        raise forms.ValidationError(f"{serial_number} Category Already Exists.")

class AddStockForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), initial=0, required=True)
    stock_type = forms.ModelChoiceField(queryset=Stock_Type.objects.all(), initial=0, required=True)
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), initial=0, required=True)

    class Meta:
        model = Stock
        fields = ['zone', 'stock_type', 'item', 'quantity']

class AddPurchaseGroupForm(forms.ModelForm):
    status = forms.ModelChoiceField(queryset=Purchase_status.objects.all(), initial=0, required=True)
    payment = forms.ModelChoiceField(queryset=Payment_sources.objects.all(), initial=0, required=True)

    class Meta:
        model = Purchase_group
        fields = ['order_number', 'tracking_url', 'shipping_cost', 'payment','status', 'standard_lead_time', 'expected_delivery_date', 'delivery_date']

class AddPurchaseForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), initial=0, required=True)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), initial=0, required=True)

    class Meta:
        model = Purchase
        fields = ['price_per_item', 'item', 'quantity', 'purchase_group', 'supplier']
