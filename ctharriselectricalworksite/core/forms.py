from django import forms
from django.forms import inlineformset_factory
from .models import Client, Invoice, Material, InvoiceMaterial


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['bill_to_name', 'bill_to_address', 'ship_to_name', 'ship_to_address', 'date', 'terms']
    
    item_description = forms.CharField(max_length=255)
    quantities = forms.IntegerField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        cleaned_data = super().clean()
        quantities = cleaned_data.get('quantities')
        price = cleaned_data.get('price')
        if quantities is not None and price is not None:
            cleaned_data['amount'] = quantities * price
        return cleaned_data

#class MaterialForm(forms.ModelForm):
#    class Meta:
#        model = Material
#        fields = ['item', 'description', 'price']
        

class ClientOnboardingForm(forms.ModelForm):
    #company_name = forms.CharField(label='Name of Company', max_length=100)
    #legal_name = forms.CharField(label='Legal Name', max_length=100)
    #contact_name = forms.CharField(label='Contact Name', max_length=100)
    #phone_number = forms.CharField(label='Phone Number', max_length=15)
    #website = forms.URLField(label='Website')
    #email = forms.EmailField(label='Email')
    #street_address = forms.CharField(label='Street Address', max_length=100)
    #city = forms.CharField(label='City', max_length=50)
    #state = forms.CharField(label='State', max_length=2)
    #zip_code = forms.CharField(label='Zip Code', max_length=10)
    #industry = forms.CharField(label='Industry', max_length=100)
    #entity = forms.CharField(label='Entity', max_length=100)
    
    class Meta:
        model = Client
        fields = ['FName', 'LName', 'email', 'contact_name', 'phone_number', 'address_street', 'address_city', 'address_state', 'address_zip']
    
    FName = forms.CharField(label='First Name', max_length=100)
    LName = forms.CharField(label='Last Name', max_length=100)
    email = forms.EmailField(label='Email')
    contact_name = forms.CharField(label='Contact Name', max_length=100)
    phone_number = forms.CharField(label='Phone Number', max_length=20)
    address_street = forms.CharField(label='Street Address', max_length=255)
    address_city = forms.CharField(label='City', max_length=100)
    address_state = forms.CharField(label='State', max_length=100)
    address_zip = forms.CharField(label='Zip Code', max_length=20)



#New invoice page - forms


class NewInvoice_EmptyForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['item', 'description', 'qty', 'price']
    item = forms.CharField(label='Item', max_length=100)
    description = forms.CharField(label='Description', max_length=100)
    qty = forms.CharField(label='qty', max_length=100)
    price = forms.CharField(label='price', max_length=100)

#~~~~~~~~~~~~~~~~~~~~~~~~~~FOR DYNAMIC FORM~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['item', 'price']
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST~~~~~~~~~~~~~~~~~~~~~~~~~~
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'status']

InvoiceMaterialFormSet = inlineformset_factory(Invoice, InvoiceMaterial, fields=('material', 'quantity'), extra=1, can_delete=True)