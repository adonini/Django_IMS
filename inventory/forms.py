from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Category, Stock, Producer, Stock_Type, Group, Item_status, Telescope, Zone, Purchase_status, Purchase_group, Purchase, Payment_sources, Supplier, Telescope_structure, PartNumber


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AddItemForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), initial=0, required=True)
    part_number = forms.CharField(required=True)
    serial_number = forms.CharField(required=False)
    price = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    producer = forms.ModelChoiceField(queryset=Producer.objects.all(), initial=0, required=False)  # to give the choice between already existing categories
    model = forms.CharField(required=False)
    expiration_date = forms.DateField(required=False)
    datasheet_url = forms.CharField(required=False)
    status = forms.ModelChoiceField(queryset=Item_status.objects.all(), initial=0, required=False) 
    telescope = forms.ModelChoiceField(queryset=Telescope_structure.objects.all(), initial=0, required=False)
    quantity = forms.FloatField(required=False)

    class Meta:
        model = Item
        fields = ['group', 'part_number', 'serial_number', 'price', 'producer', 'expiration_date', 'model', 'datasheet_url', 'status', 'telescope', 'quantity']

    def clean_part_number(self):
        part_number_input = self.cleaned_data['part_number']
        if isinstance(part_number_input, PartNumber):
            return part_number_input
        group=self.cleaned_data['group']
        part_number_instance, created = PartNumber.objects.get_or_create(code=part_number_input, group=group)
        return part_number_instance
    
    def save(self, commit=True):
        instance = super(AddItemForm, self).save(commit=False)
        instance.part_number = self.cleaned_data['part_number']
        if commit:
            instance.save()
        return instance

    # Here the code looks for an existing code same as the one inserted - celan_{field} is a django system to execute extra validations on some fields.
#    def clean_code(self):
#        id = self.instance.id if self.instance.id else 0
#        code = self.cleaned_data['code']
#        try:
#            if int(id) > 0:
#                item = Item.objects.exclude(id=id).get(code=code)
#            else:
#                item = Item.objects.get(code=code)
#        except:
#            return code
#        raise forms.ValidationError(f"{code} Category Already Exists.")
#    
#    def clean_serial_number(self):
#        id = self.instance.id if self.instance.id else 0
#        serial_number = self.cleaned_data['serial_number']
#        try:
#            if int(id) > 0:
#                item = Item.objects.exclude(id=id).get(serial_number=serial_number)
#            else:
#                item = Item.objects.get(serial_number=serial_number)
#        except:
#            return serial_number
#        raise forms.ValidationError(f"{serial_number} Category Already Exists.")

class AddStockForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), initial=0, required=True)
    stock_type = forms.ModelChoiceField(queryset=Stock_Type.objects.all(), initial=0, required=True)
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), initial=0, required=True)
    quantity = forms.IntegerField(required=True)

    class Meta:
        model = Stock
        fields = ['zone', 'stock_type', 'item', 'quantity']

class ModifyStockForm(forms.ModelForm):
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), initial=0, required=True)

    class Meta:
        model = Stock
        fields = ['zone']

class AddPurchaseGroupForm(forms.ModelForm):
    status = forms.ModelChoiceField(queryset=Purchase_status.objects.all(), initial=0, required=False)
    payment = forms.ModelChoiceField(queryset=Payment_sources.objects.all(), initial=0, required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), initial=0, required=True)
    standard_lead_time = forms.IntegerField(required=False)
    # Here I can specify the fields requiered

    class Meta:
        model = Purchase_group
        fields = ['order_number', 'tracking_url', 'shipping_cost', 'payment', 'status', 'supplier', 'standard_lead_time', 'expected_delivery_date', 'delivery_date', 'order_date']

class AddPurchaseForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), initial=0, required=True)
    quantity = forms.IntegerField(required=False)

    class Meta:
        model = Purchase
        fields = ['price_per_item', 'item', 'quantity', 'purchase_group']
