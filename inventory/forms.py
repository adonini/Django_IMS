from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Item, Category, Stock, Producer, Stock_Type


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AddItemForm(forms.ModelForm):
    producer = forms.ModelChoiceField(queryset=Producer.objects.all(), initial=0, required=False)  # to give the choice between already existing categories

    class Meta:
        model = Item
        fields = '__all__'
        #fields = ['code', 'name', 'description', 'category', 'producer', 'model', 'serials']  # '__all__' if wanna get all the fields in the model

    # Here the code looks for an existing code same as the one inserted
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
    type = forms.ModelChoiceField(queryset=Stock_Type.objects.all(), initial=0, required=True)

    class Meta:
        model = Stock
        fields = '__all__'
        #fields = ['item', 'quantity', 'area', 'shelf', 'type', 'price']


    def clean_item(self):
        pid = self.cleaned_data['item']
        try:
            item = Item.objects.get(id=pid)
            return item
        except:
            raise forms.ValidationError("Item is not valid")
