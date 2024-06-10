from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from .models import Client, Invoice, Material, InvoiceMaterial, UserInfo

class ClientForm(forms.ModelForm):
    class Meta:    
        model = Client
        fields = '__all__'

class DateInput(forms.DateInput):
    input_type = 'date'
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

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')        

class ClientOnboardingForm(forms.ModelForm):    
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





#~~~~~~~~~~~~~~~~~~~~~~~~~~FOR ADMIN / PERSONAL INFO~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['ship_to_name', 'ship_to_address', 'ship_to_city', 'ship_to_state', 'ship_to_zip', 'email_address', 'phone_number', 'markup_value', 'invoice_terms']
    ship_to_name = forms.CharField(label='Name', max_length=100)
    ship_to_address = forms.CharField(label='Address', max_length=255)
    ship_to_city = forms.CharField(label='City', max_length=100)
    ship_to_state = forms.CharField(label='State', max_length=100)
    ship_to_zip = forms.CharField(label='Zip Code', max_length=20)
    email_address = forms.EmailField(label='Email')
    phone_number = forms.CharField(label='Phone Number', max_length=20)
    markup_value = forms.DecimalField(label='Markup Value', max_digits=4, decimal_places=2)
    invoice_terms = forms.CharField(label='Invoice Terms', max_length=20)

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
        fields = ['item', 'description', 'price']
    description = forms.CharField(label='Description', max_length=100)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TEST~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'status', 'date', 'ship_to_name', 'ship_to_address', 'ship_to_city', 'ship_to_state', 'ship_to_zip', 'bill_to_name', 'bill_to_address', 'bill_to_city', 'bill_to_state', 'bill_to_zip']
        widgets = {
            "date": forms.DateInput(attrs={"id": "datepicker", 'autocomplete':'off'}),
            'client': forms.Select(attrs={'class': 'ClientSelect'}),
        }
    ship_to_name = forms.CharField(label='Ship to Name', max_length=100, required=False)
    ship_to_address = forms.CharField(label='Ship to Address', max_length=255, required=False)
    ship_to_city = forms.CharField(label='Ship to City', max_length=100, required=False)
    ship_to_state = forms.CharField(label='Ship to State', max_length=100, required=False)
    ship_to_zip = forms.CharField(label='Ship to Zip Code', max_length=20, required=False)

    bill_to_name = forms.CharField(label='Bill to Name', max_length=100, required=False)
    bill_to_address = forms.CharField(label='Bill to Address', max_length=255, required=False)
    bill_to_city = forms.CharField(label='Bill to City', max_length=100, required=False)
    bill_to_state = forms.CharField(label='Bill to State', max_length=100, required=False)
    bill_to_zip = forms.CharField(label='Bill to Zip Code', max_length=20, required=False)


class InvoiceMaterialForm(forms.ModelForm):
    class Meta:
        model = InvoiceMaterial
        fields = (
                'material', 'quantity', 'markup'
        )
        widgets = {
            'material': forms.Select(attrs={'class': 'MaterialSelection'}),
            'deletion_widget': forms.CheckboxInput(attrs={'class': 'delete-checkbox'}), # Hide the delete checkbox
        }

InvoiceMaterialFormSet = inlineformset_factory(Invoice, InvoiceMaterial,  form = InvoiceMaterialForm, extra=1, can_delete=True)