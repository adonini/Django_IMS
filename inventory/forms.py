from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Category, StockItem, Producer, StockOPTypes


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AddItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), initial=0, required=False)  # to give the choice between already existing categories
    producer = forms.ModelChoiceField(queryset=Producer.objects.all(), initial=0, required=False)  # to give the choice between already existing categories

    class Meta:
        model = Item
        fields = ['code', 'name', 'description', 'category', 'producer', 'model', 'serials']  # '__all__' if wanna get all the fields in the model

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


class AddStockForm(forms.ModelForm):
    item = forms.CharField(max_length=30)
    quantity = forms.CharField(max_length=250)
    type = forms.ModelChoiceField(queryset=StockOPTypes.objects.all(), initial=0, required=True)

    class Meta:
        model = StockItem
        fields = ['item', 'quantity', 'area', 'shelf', 'type', 'price']

    def clean_item(self):
        pid = self.cleaned_data['item']
        print('PID: ', pid)
        try:
            item = Item.objects.get(id=pid)
            print(item)
            return item
        except:
            raise forms.ValidationError("Item is not valid")
