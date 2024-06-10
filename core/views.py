from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, Material, Invoice, InvoiceMaterial, UserInfo
from django.db.models import Q
from django.forms import modelformset_factory
from .forms import  ClientOnboardingForm, ClientForm, InvoiceForm, MaterialForm, NewInvoice_EmptyForm, InvoiceMaterialFormSet, UserInfoForm
from django.urls import reverse
from datetime import date, timedelta, datetime
import calendar
import time
from decimal import *
from django.contrib import messages

#PDF GENERATION IMPORTS
from django.http import JsonResponse, HttpResponseRedirect, FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.core.exceptions import MultipleObjectsReturned

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa


#EMAIL IMPORTS
from django.core.mail import send_mail

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context




#Homepage - Invoice Table
def ClientInfo(request):
    clients = Client.objects.all()
    return render(request, 'index.html', {'user': clients})

def index(request):
    search_query = request.GET.get('search')

    if search_query:
        invoices = Invoice.objects.filter(
            Q(status__icontains=search_query) | 
            Q(client__FName__icontains=search_query) |
            Q(client__LName__icontains=search_query)
        )
    else:
        invoices = Invoice.objects.all()

    return render(request, 'index.html', {'invoices': invoices})
#Invoice page 

def invoice_page(request):
    invoice = Invoice.objects.all()
    return render(request, 'invoice.html', {'invoices': invoice})

def invoice_search(request):
    search_query = request.GET.get('search')

    if search_query:
        invoices = Invoice.objects.filter(
            Q(client__FName__icontains=search_query) |
            Q(client__LName__icontains=search_query) |
            Q(client__email__icontains=search_query) |
            Q(client__contact_name__icontains=search_query) |
            Q(client__phone_number__icontains=search_query) |
            Q(client__address_street__icontains=search_query) |
            Q(client__address_city__icontains=search_query) |
            Q(client__address_state__icontains=search_query) |
            Q(client__address_zip__icontains=search_query)
        )
    else:
        invoices = Invoice.objects.all()

    return render(request, 'invoice.html', {'invoices': invoices})

#materials
def materials_list(request):
    search_query = request.GET.get('search')

    if search_query:
        materials = Material.objects.filter(
            Q(item__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(price__icontains=search_query)
        )
    else:
        sort_by = request.GET.get('sort', 'item')
        current_order = request.session.get('current_sort_order', 'asc')
        if sort_by == request.session.get('last_sort_column'):
            current_order = 'desc' if current_order == 'asc' else 'asc'
        else:
            current_order = 'asc'
        request.session['last_sort_column'] = sort_by
        request.session['current_sort_order'] = current_order
        sort_by = f"-{sort_by}" if current_order == 'desc' else sort_by
        materials = Material.objects.all().order_by(sort_by)

    return render(request, 'materials.html', {'materials': materials})

def intake_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('materials_list')
    else:
        form = MaterialForm()
    return render(request, 'materialsintakeform.html', {'form': form})

def materials_edit(request, material_id):
    material = get_object_or_404(Material, id=material_id)

    if request.method == 'POST':
        if 'update' in request.POST:
            form = MaterialForm(request.POST, instance=material)
            if form.is_valid():
                form.save()
                return redirect('materials_list')
        elif 'delete' in request.POST:
            material.delete()
            return redirect('materials_list')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'materials_edit.html', {'form': form, 'material': material})

#Client
# Retrieve all clients from the database and pass them to the client template
def client_list(request):
    search_query = request.GET.get('search')

    if search_query:
        clients = Client.objects.filter(
            Q(FName__icontains=search_query) |
            Q(LName__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(contact_name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(address_street__icontains=search_query) |
            Q(address_city__icontains=search_query) |
            Q(address_state__icontains=search_query) |
            Q(address_zip__icontains=search_query)
        )
    else:
        sort_by = request.GET.get('sort', 'FName')
        current_order = request.session.get('current_sort_order', 'asc')
        if sort_by == request.session.get('last_sort_column'):
            current_order = 'desc' if current_order == 'asc' else 'asc'
        else:
            current_order = 'asc'
        request.session['last_sort_column'] = sort_by
        request.session['current_sort_order'] = current_order
        sort_by = f"-{sort_by}" if current_order == 'desc' else sort_by
        clients = Client.objects.all().order_by(sort_by)

    return render(request, 'client.html', {'clients': clients})


def client_onboarding_page(request):
    if request.method == 'POST':
        form = ClientOnboardingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the index page after successful submission
    else:
        form = ClientOnboardingForm()
    return render(request, 'clientonboardingform.html', {'form': form})
#client edit function
def client_edit(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        if 'update' in request.POST:
            form = ClientForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                return redirect('client_list')
        elif 'delete' in request.POST:
            client.delete()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)

    return render(request, 'client_edit.html', {'form': form, 'client': client})

#Invoice
def invoice_page_form(request): #Depricated invoice form possibly
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        if invoice_form.is_valid():
            # Save the form data to the database
            invoice = invoice_form.save(commit=False)
            
            # Calculate the amount
            amount = invoice.quantity * invoice.price
            invoice.amount = amount
            
            # Calculate the subtotal
            subtotal = amount
            
            # Calculate the tax
            tax_rate = 0.25  # Assuming tax rate is 0.25%
            tax = subtotal * (tax_rate / 100)
            
            # Calculate the total
            total = subtotal + tax
            
            # Set the calculated values to the invoice object
            invoice.subtotal = subtotal
            invoice.tax = tax
            invoice.total = total
            invoice.balance_due = total
            
            # Save the invoice to the database
            invoice.save()
            
            # Redirect to a success page or other actions as needed
            return redirect('invoice_page')  # Redirect to the same page after submission
    else:
        invoice_form = InvoiceForm()
    return render(request, 'invoice.html', {'invoice_form': invoice_form})

#~~~~~~~~~~~~~~~~~~~~~~CALENDAR~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Utility functions
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def prev_month_url(year, month):
    first_day_current_month = date(year, month, 1)
    prev_month = first_day_current_month - timedelta(days=1)
    return reverse('calendar_page', args=(prev_month.year, prev_month.month))

def next_month_url(year, month):
    days_in_current_month = calendar.monthrange(year, month)[1]
    first_day_next_month = date(year, month, 1) + timedelta(days=days_in_current_month)
    return reverse('calendar_page', args=(first_day_next_month.year, first_day_next_month.month))



#----------------------------------------------------------------------


# Calendar view
def calendar_page(request, year=None, month=None):
    today = datetime.today()

    if year is None or month is None:
        today = date.today()
        year, month = today.year, today.month
    else:
        year, month = int(year), int(month)

    # Generate the month_calendar variable
    month_calendar = generate_month_calendar(year, month)

    # Prepare the context data for the template
    context = {
        'current_year': year,
        'current_month': month,
        'month_calendar': month_calendar,
        'previous_month_url': prev_month_url(year, month),
        'next_month_url': next_month_url(year, month),
        
    }

    return render(request, 'calendar.html', context)

# Function to generate the calendar
def generate_month_calendar(year, month):
    cal = calendar.Calendar()

    month_calendar = []
    for week in cal.monthdatescalendar(year, month):
        week_list = []
        for day in week:
            day_invoices = []  # Prepare a list to hold invoices for the day
            if day.month == month:
                # Fetch invoices for the day and add them to the list
                day_invoices = get_invoice_for_date(day)  
            week_list.append({'date': day, 'invoices': day_invoices})
        month_calendar.append(week_list)

    return month_calendar

def get_invoice_for_date(date):
    invoices = Invoice.objects.filter(date=date)
    return invoices
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~END CALENDAR~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#proposal page
from .forms import InvoiceForm, MaterialForm, ClientOnboardingForm, InvoiceMaterialFormSet
from .models import Client

from django.shortcuts import redirect, render
from .forms import InvoiceForm, MaterialForm, ClientOnboardingForm, InvoiceMaterialFormSet
from .models import Client

#New Invoice Page
def new_invoice(request):
    client_list = Client.objects.all()
    #~~~~~~~~~~status logic~~~~~~~~~~~~~~
    initial_status = request.GET.get('status', Invoice.DRAFT)  # Default to 'Draft' if not specified
    if initial_status not in dict(Invoice.INVOICE_STATUS).keys():
        initial_status = Invoice.DRAFT  # Fallback to 'Draft' if the status is invalid
    if initial_status == Invoice.PROPOSAL:
        page_title = "Proposal"
    elif initial_status == Invoice.DRAFT:
        page_title = "Draft"
    elif initial_status == Invoice.OPEN:
        page_title = "Invoice"
    else:
        page_title = "Invoice"  # Default title
    #~~~~~~~~~end status logic~~~~~~~~~~~
    if request.method == 'POST':
        Invoice_Form = InvoiceForm(request.POST)
        Material_Form = MaterialForm(request.POST)
        ClientOnboarding_Form = ClientOnboardingForm(request.POST)

        if ClientOnboarding_Form.is_valid():
            new_client = ClientOnboarding_Form.save()
            messages.success(request, f"{new_client} has been successfully added.")
            redirect_url = f"{reverse('new_invoice')}?status={initial_status}"
            return HttpResponseRedirect(redirect_url)
        
        elif Material_Form.is_valid():
            new_material = Material_Form.save()
            messages.success(request, f"{new_material} has been successfully added.")
            redirect_url = f"{reverse('new_invoice')}?status={initial_status}"
            return HttpResponseRedirect(redirect_url)
        


        elif Invoice_Form.is_valid():
            CleanData = Invoice_Form.cleaned_data['client']
            print(CleanData.id)

            SpecifiedClient = Client.objects.filter(pk = CleanData.id)
            for i in SpecifiedClient:
                print(i)
            
            invoice = Invoice_Form.save()

            Invoice_FormSet = InvoiceMaterialFormSet(request.POST, instance=invoice)
            if Invoice_FormSet.is_valid():
                Invoice_FormSet.save()
                messages.success(request, f"{invoice.client} {page_title} Created")
                return redirect('/invoice')
    else:
        Invoice_Form = InvoiceForm(initial={'status': initial_status})
        Invoice_FormSet = InvoiceMaterialFormSet()
        Material_Form = MaterialForm()
        ClientOnboarding_Form = ClientOnboardingForm()

    return render(request, 'new_invoice.html', {'client_list': client_list, 'NewMaterial': Material_Form, 'NewCustomer': ClientOnboarding_Form, 'Invoice_Form': Invoice_Form, 'Invoice_FormSet': Invoice_FormSet, 'title': page_title})






def new_proposal(request):
    if request.method == 'POST':
        Invoice_Form = InvoiceForm(request.POST)

        ClientOnboarding_Form = ClientOnboardingForm(request.POST)

        if ClientOnboarding_Form.is_valid():
            ClientOnboarding_Form.save()
            return redirect('/proposal_form')  # Redirect to the index page after successful submission
        
        elif Invoice_Form.is_valid():
            invoice = Invoice_Form.save()
            Invoice_FormSet = InvoiceMaterialFormSet(request.POST, instance=invoice)
            
            if Invoice_FormSet.is_valid():
                Invoice_FormSet.save()
                return redirect('/invoice')
    else:
        Invoice_Form = InvoiceForm()
        Invoice_FormSet = InvoiceMaterialFormSet()

        ClientOnboarding_Form = ClientOnboardingForm()


    return render(request, 'proposalform.html', {'NewCustomer': ClientOnboarding_Form, 'Invoice_Form': Invoice_Form, 'Invoice_FormSet': Invoice_FormSet})







#~~~~~~~~~~~~FOR DYNAMIC INVOICE FORM~~~~~~~~~~~~~~~~~~~~~~~~
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            formset = InvoiceMaterialFormSet(request.POST, instance=invoice)
            if formset.is_valid():
                for delete_value in formset.deleted_objects:
                    delete_value.delete()
                formset.save()
                return redirect('index')
    else:
        form = InvoiceForm()
        formset = InvoiceMaterialFormSet()
    return render(request, 'invoice_form.html', {'form': form, 'formset': formset})
#~~~~~~~~~~~~END DYNAMIC INVOICE FORM~~~~~~~~~~~~~~~~~~~~~~~~






#~~~~~~~~~~~~~~~~~~~~~EDITING INVOICE~~~~~~~~~~~~~~~~~~~~~~~~
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction

@require_http_methods(["GET", "POST"])
def invoice_edit(request, invoice_id):
    Material_ID = Material.objects.all()
    
    ClientInfo = Client.objects.all()


    User = UserInfo.objects.all()
    for i in User:
        U_ID = i.id
    Static_User_Info = UserInfo.objects.get(pk=U_ID)
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice_date = invoice.date.strftime('%Y-%m-%d')
    material_list = []
    if request.method == "POST":

        Invoice_Form = InvoiceForm(request.POST, instance=invoice)

        if Invoice_Form.is_valid():
            invoice = Invoice_Form.save()


        invoice.save()
        # Handling updates to InvoiceMaterial items
        LineItemFormset = InvoiceMaterialFormSet(request.POST, instance=invoice)
        



        for form in LineItemFormset:  
            print(form['DELETE'].value())
            if form['DELETE'].value() == True:
                form.instance.delete()
                print('Deleted')

            if form.is_valid():
                form.instance.save()
                print('valid')
            elif form.is_valid() == False:
                print('invalid')
        if LineItemFormset.is_valid():
            print('LineItemFormset is valid')
            LineItemFormset.save()

        print(LineItemFormset.errors)
        #LineItemFormset.save()
        messages.success(request, f"{invoice} successfully updated")

        return redirect('invoice_edit', invoice_id)
                
        

    else:
        Invoice_Form = InvoiceForm(instance=invoice)

        

        invoice_materials = InvoiceMaterial.objects.filter(invoice=invoice)
        formsetcount =  InvoiceMaterial.objects.filter(invoice=invoice).count() + 1
        materials = Material.objects.all()
        source_page = request.GET.get('source', None)  # Get the source page parameter
        LineItemFormset = InvoiceMaterialFormSet(instance=invoice)
        LineItemFormset_empty = InvoiceMaterialFormSet()

        edit_context = {
            'invoicematerial-TOTAL_FORMS' : formsetcount,
            'Line_Item_Formset' : LineItemFormset,
            'Static_User_Info': Static_User_Info,
            'invoice': invoice,
            'invoice_materials': invoice_materials,
            'materials': materials,
            'invoice_date': invoice_date,
            'source_page': source_page,
            'Invoice_Form': Invoice_Form,
            'LineItemFormset_empty': LineItemFormset_empty,
            'ClientInfo': ClientInfo
        }
        return render(request, 'invoice_edit.html', edit_context)

@require_POST
def invoice_material_delete(request, item_id):
    item = get_object_or_404(InvoiceMaterial, pk=item_id)
    item.delete()
    return JsonResponse({'status': 'success', 'message': 'Item deleted successfully.'})


#Changing invoice status in row
def invoice_change_status(request, invoice_id):
    invoice_data = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == 'GET':
        if invoice_data.status == 'Draft':
            new_status = 'Proposal'
        elif invoice_data.status == 'Proposal':
            new_status = 'Open'
        elif invoice_data.status == 'Open':
            new_status = 'Closed'
        else:
            messages.error(request, "Status update not allowed for this invoice.")
            return redirect('invoice_page')
        # Update the status and save
        invoice_data.status = new_status
        invoice_data.save()
        messages.success(request, f"{invoice_data.client} status changed to \"{new_status}\".")
        return redirect('invoice_page')
    return redirect('invoice_page')
    
#~~~~~~~~~~~~~~~~~~~~~EDITING INVOICE~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~DELETE INVOICE~~~~~~~~~~~~~~~~~~~~~~~~
def invoice_delete(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    client = invoice.client
    pk = invoice_id
    if invoice.delete():
        messages.success(request, f"Invoice #{pk} ({client}) has been succesfully deleted")
        return redirect('index')
    else:
        messages.error(request, "Error occured, could not delete Invoice #{pk} ({client})")
        return redirect('index')




#~~~~~~~~~~~~~~~~~~~~~ NEW PDF GENERATION ~~~~~~~~~~~~~~~~~~~~~~~~
#Testing Data
data = {
    'FName': 'John',
    'LName': 'Doe',
    'invoice_id': '1234',
    'date': '2021-01-01',
    'line_items': ['item1', 'item2', 'item3'],
    'subtotal': '100',
    'tax': '25',
    'total': '125',
    'balance_due': '125'
}


    
def InvoicePDF(request):
    invoice_id = '26'

    InvoiceData = Invoice.objects.get(pk=invoice_id)
    Invoice_Material = InvoiceMaterial.objects.filter(invoice = invoice_id)
    Item_Dict = {}
    Invoice_Total = []
    ItemMarkup_Tax_Fee = []

    for item in Invoice_Material:
            if item.markup == True:
                Item_Total = item.material.price * item.quantity
                Item_Total_Markup = Item_Total * Static_User_Info.markup_value
                Item_Total_Markup = round(Decimal(Item_Total_Markup), 2)
                ItemMarkupValue = Item_Total_Markup - Item_Total

                ItemMarkup_Tax_Fee.append(ItemMarkupValue)
                Invoice_Total.append(Item_Total_Markup)
                Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total_Markup}

            else:
                Item_Total = item.material.price * item.quantity
                Invoice_Total.append(Item_Total)
                Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total}

    #MATH FUNCTIONS FOR INVOICE



    
    Invoice_Subtotal = sum(Invoice_Total)
    
    tax = sum(ItemMarkup_Tax_Fee)
    tax = tax = round(Decimal(tax), 2)


    #MATH FUNCTIONS FOR INVOICE
    
    Invoice_Total = sum(Invoice_Total)
    
    tax_ratio = Decimal(0.05)
    tax = Decimal(Invoice_Total) * tax_ratio
    tax = round(Decimal(tax), 2)

    subtotal = Decimal(tax) + Decimal(Invoice_Total)

    curr_date = str(datetime.today().strftime('%Y-%m-%d'))

        
    data = {
        'FName': InvoiceData.client.FName,
        'LName': InvoiceData.client.LName,
        'invoice_id': InvoiceData.id,
        'date': curr_date,
        # terms = 
        'bill_to_name': InvoiceData.client,
        'bill_to_address': InvoiceData.client.address_street,
        'bill_to_city': InvoiceData.client.address_city,
        'bill_to_state': InvoiceData.client.address_state,
        'bill_to_zip': InvoiceData.client.address_zip,
        'line_items': Invoice_Material,
        'Item_Dict': Item_Dict,
        'total': Invoice_Total,
        'tax': tax,
        'subtotal': subtotal,
    }

    return render(request, 'InvoicePDF.html', {'data':data})


#~~~~~~~~~~~~~~~~~~~~~ END NEW PDF GENERATION ~~~~~~~~~~~~~~~~~~~~~~~~

def render_to_pdf(template_src, PDF_Name, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf_name = PDF_Name
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        with open('PDF_Archive/'+ pdf_name, 'wb') as output:
            pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), output)        
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class ViewPDF(View):
    def get(self, request, invoice_id, *args, **kwargs):
        User = UserInfo.objects.all()
        for i in User:
            U_ID = i.id
        Static_User_Info = UserInfo.objects.get(pk=U_ID)

        InvoiceData = Invoice.objects.get(pk=invoice_id)
        Invoice_Material = InvoiceMaterial.objects.filter(invoice = invoice_id)
        Item_Dict = {}
        Invoice_Total = []
        BillingInfo = []
        ShippingInfo = []
        ItemMarkup_Tax_Fee = []

        

        BillingInfo = [InvoiceData.bill_to_name, 
                       InvoiceData.bill_to_address, 
                       InvoiceData.bill_to_city, 
                       InvoiceData.bill_to_state, 
                       InvoiceData.bill_to_zip]
        
        ShippingInfo = [InvoiceData.ship_to_name, 
                        InvoiceData.ship_to_address, 
                        InvoiceData.ship_to_city, 
                        InvoiceData.ship_to_state, 
                        InvoiceData.ship_to_zip]


#Checks if billing info is empty and if so uses client info
        if any( i is None for i in BillingInfo) == True or any( i is '' for i in ShippingInfo) == True:
            BillingInfo = [InvoiceData.client, InvoiceData.client.address_street, InvoiceData.client.address_city, InvoiceData.client.address_state, InvoiceData.client.address_zip]
        else:
            BillingInfo = [InvoiceData.bill_to_name, InvoiceData.bill_to_address, InvoiceData.bill_to_city, InvoiceData.bill_to_state, InvoiceData.bill_to_zip]
        
        if any( i is None for i in ShippingInfo) == True or any( i is '' for i in ShippingInfo) == True:
            ShippingInfo = [InvoiceData.client, InvoiceData.client.address_street, InvoiceData.client.address_city, InvoiceData.client.address_state, InvoiceData.client.address_zip]
            
        else:
            ShippingInfo = [InvoiceData.ship_to_name, InvoiceData.ship_to_address, InvoiceData.ship_to_city, InvoiceData.ship_to_state, InvoiceData.ship_to_zip]



        for item in Invoice_Material:
                if item.markup == True:
                    Item_Total = item.material.price * item.quantity
                    Item_Total_Markup = Item_Total * Static_User_Info.markup_value
                    Item_Total_Markup = round(Decimal(Item_Total_Markup), 2)
                    ItemMarkupValue = Item_Total_Markup - Item_Total

                    ItemMarkup_Tax_Fee.append(ItemMarkupValue)
                    Invoice_Total.append(Item_Total_Markup)
                    Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total_Markup}

                else:
                    Item_Total = item.material.price * item.quantity
                    Invoice_Total.append(Item_Total)
                    Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total}


        #MATH FUNCTIONS FOR INVOICE
        
        Invoice_Subtotal = sum(Invoice_Total)
        
        tax = sum(ItemMarkup_Tax_Fee)
        tax = tax = round(Decimal(tax), 2)

        total = Decimal(tax) + Decimal(Invoice_Subtotal)
    
        curr_date = str(datetime.today().strftime('%Y-%m-%d'))
        print(BillingInfo[1])
            
        data = {
            'FName': InvoiceData.client.FName,
            'LName': InvoiceData.client.LName,
            'invoice_id': InvoiceData.id,
            'date': curr_date,
            # either ship to or bill to needs to be from the client / the other should have the ability to be edited
            # Right now the shipping info is always from client and billing info is dynamic (either from client or user input)

            'ship_to_name': ShippingInfo[0],
            'ship_to_address': ShippingInfo[1],
            'ship_to_city': ShippingInfo[2],
            'ship_to_state': ShippingInfo[3],
            'ship_to_zip': ShippingInfo[4],

            #assignes billing info to list location from above if statment - Maybe make dict?#####################
            'bill_to_name': BillingInfo[0],
            'bill_to_address': BillingInfo[1],
            'bill_to_city': BillingInfo[2],
            'bill_to_state': BillingInfo[3],
            'bill_to_zip': BillingInfo[4],

            'invoice_all': InvoiceData,
            'line_items': Invoice_Material,
            'Item_Dict': Item_Dict,
            'subtotal': Invoice_Subtotal,
            'tax': tax,
            'total': total,
            'Static_User_Info': Static_User_Info,
        }
        PDF_Name = str(InvoiceData.id) + '_' + InvoiceData.client.FName + '_' + InvoiceData.client.LName + '_' + curr_date + '_' + InvoiceData.status + '.pdf'
        pdf = render_to_pdf('InvoicePDF.html', PDF_Name, data)
        return HttpResponse(pdf, content_type='application/pdf')
    
        #filename=str(InvoiceData.id) + '_' + InvoiceData.client.FName + '_' + InvoiceData.client.LName + '_' + curr_date + '.pdf'



def InvoiceFinalize(request, invoice_id):

    User = UserInfo.objects.all()
    for i in User:
        U_ID = i.id
    Static_User_Info = UserInfo.objects.get(pk=U_ID)
    
    print(invoice_id)
    InvoiceData = Invoice.objects.get(pk=invoice_id)

    Invoice_Material = InvoiceMaterial.objects.filter(invoice = invoice_id)
    Item_Dict = {}
    Invoice_Total = []
    BillingInfo = []
    ShippingInfo = []
    ItemMarkup_Tax_Fee = []
   

    BillingInfo = [InvoiceData.bill_to_name, InvoiceData.bill_to_address, InvoiceData.bill_to_city, InvoiceData.bill_to_state, InvoiceData.bill_to_zip]
    ShippingInfo = [InvoiceData.ship_to_name, InvoiceData.ship_to_address, InvoiceData.ship_to_city, InvoiceData.ship_to_state, InvoiceData.ship_to_zip]

    if InvoiceData.bill_to_name is '':
        print('none')

#Checks if billing info is empty and if so uses client info
    if any( i is None for i in BillingInfo) == True or any( i is '' for i in BillingInfo) == True:
        BillingInfo = [InvoiceData.client, InvoiceData.client.address_street, InvoiceData.client.address_city, InvoiceData.client.address_state, InvoiceData.client.address_zip]
    else:
        BillingInfo = [InvoiceData.bill_to_name, InvoiceData.bill_to_address, InvoiceData.bill_to_city, InvoiceData.bill_to_state, InvoiceData.bill_to_zip]
 
    if any( i is None for i in ShippingInfo) == True or any( i is '' for i in ShippingInfo) == True:
        ShippingInfo = [InvoiceData.client, InvoiceData.client.address_street, InvoiceData.client.address_city, InvoiceData.client.address_state, InvoiceData.client.address_zip]
    else:
        ShippingInfo = [InvoiceData.ship_to_name, InvoiceData.ship_to_address, InvoiceData.ship_to_city, InvoiceData.ship_to_state, InvoiceData.ship_to_zip]



    for item in Invoice_Material:
        if item.markup == True:
            Item_Total = item.material.price * item.quantity
            Item_Total_Markup = Item_Total * Static_User_Info.markup_value
            Item_Total_Markup = round(Decimal(Item_Total_Markup), 2)
            ItemMarkupValue = Item_Total_Markup - Item_Total

            ItemMarkup_Tax_Fee.append(ItemMarkupValue)
            Invoice_Total.append(Item_Total_Markup)
            Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total_Markup}

        else:
            Item_Total = item.material.price * item.quantity
            Invoice_Total.append(Item_Total)
            Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total}

    #MATH FUNCTIONS FOR INVOICE



    
    Invoice_Subtotal = sum(Invoice_Total)
    
    tax = sum(ItemMarkup_Tax_Fee)
    tax = tax = round(Decimal(tax), 2)


    total = Decimal(tax) + Decimal(Invoice_Subtotal)

    curr_date = str(datetime.today().strftime('%Y-%m-%d'))
        
    data = {
        'FName': InvoiceData.client.FName,
        'LName': InvoiceData.client.LName,
        'invoice_id': InvoiceData.id,
        'date': curr_date,
        # either ship to or bill to needs to be from the client / the other should have the ability to be edited
        # Right now the shipping info is always from client and billing info is dynamic (either from client or user input)

        'ship_to_name': ShippingInfo[0],
        'ship_to_address': ShippingInfo[1],
        'ship_to_city': ShippingInfo[2],
        'ship_to_state': ShippingInfo[3],
        'ship_to_zip': ShippingInfo[4],

        #assignes billing info to list location from above if statment - Maybe make dict?#####################
        'bill_to_name': BillingInfo[0],
        'bill_to_address': BillingInfo[1],
        'bill_to_city': BillingInfo[2],
        'bill_to_state': BillingInfo[3],
        'bill_to_zip': BillingInfo[4],

        'invoice_all': InvoiceData,
        'line_items': Invoice_Material,
        'Item_Dict': Item_Dict,
        'subtotal': Invoice_Subtotal,
        'tax': tax,
        'total': total,
        'Static_User_Info': Static_User_Info,
    }
    PDF_Name = str(InvoiceData.id) + '_' + InvoiceData.client.FName + '_' + InvoiceData.client.LName + '_' + curr_date + '_' + InvoiceData.status + '.pdf'


    if request.method == 'POST':
        render_to_pdf('InvoicePDF.html', PDF_Name, data)
        if InvoiceData.status == 'Draft':
            Invoice.objects.filter(pk=invoice_id).update(status='Proposal')
        if InvoiceData.status == 'Proposal':
            Invoice.objects.filter(pk=invoice_id).update(status='Open')
        print(InvoiceData.client.email)
        subject, from_email, to = 'Subject', 'c.t.harriselectrical@gmail.com', 'gilbertrfh@gmail.com'
        html_message = render_to_string('EmailTemplate.html', {'context': 'values'})
        plainttext = 'C.T. Harris Electrical'
        template = get_template('EmailTemplate.html')
        msg = EmailMultiAlternatives(subject, plainttext, from_email, [to])

        attachment = open('PDF_Archive/'+ PDF_Name, 'rb')
        msg.attach(InvoiceData.client.FName + '_' + InvoiceData.client.LName + '_' + curr_date + '_' + InvoiceData.status + '.pdf', attachment.read(), 'application/pdf')
        
        msg.attach_alternative(template.render(data), "text/html")
        msg.send()
        messages.success(request, 'Email Sent Successful')
        return redirect('invoice_page')

    return render(request, 'Invoice_Finalize.html', {'data':data, 'Materials':Item_Dict, 'client_info': InvoiceData, })


def EmailTemplate(request):


    User = UserInfo.objects.all()
    for i in User:
        U_ID = i.id
    Static_User_Info = UserInfo.objects.get(pk=U_ID)
    
    print(invoice_id)

    InvoiceData = Invoice.objects.get(pk=invoice_id)

    print(InvoiceData.id)
    Invoice_Material = InvoiceMaterial.objects.filter(invoice = invoice_id)
    Item_Dict = {}
    Invoice_Total = []
    BillingInfo = []
    ShippingInfo= []

    for item in Invoice_Material:
        Item_Total = item.material.price * item.quantity
        Invoice_Total.append(Item_Total)

        Item_Dict[item.material.item] = {'material': item.material.item, 'description':item.material.description, 'quantity': item.quantity, 'price': item.material.price, 'total': Item_Total}


    BillingInfo = [InvoiceData.bill_to_name, InvoiceData.bill_to_address, InvoiceData.bill_to_city, InvoiceData.bill_to_state, InvoiceData.bill_to_zip]
    ShippingInfo = [InvoiceData.ship_to_name, InvoiceData.ship_to_address, InvoiceData.ship_to_city, InvoiceData.ship_to_state, InvoiceData.ship_to_zip]


#Checks if billing info is empty and if so uses client info
    if any( i is None for i in BillingInfo) == True:
        BillingInfo = [InvoiceData.client, InvoiceData.client.address_street, InvoiceData.client.address_city, InvoiceData.client.address_state, InvoiceData.client.address_zip]
    else:
        BillingInfo = [InvoiceData.bill_to_name, InvoiceData.bill_to_address, InvoiceData.bill_to_city, InvoiceData.bill_to_state, InvoiceData.bill_to_zip]
    if any( i is None for i in ShippingInfo) == True or any( i is '' for i in ShippingInfo) == True:
        ShippingInfo = [InvoiceData.client, InvoiceData.client.address_street, InvoiceData.client.address_city, InvoiceData.client.address_state, InvoiceData.client.address_zip]
    else:
        ShippingInfo = [InvoiceData.ship_to_name, InvoiceData.ship_to_address, InvoiceData.ship_to_city, InvoiceData.ship_to_state, InvoiceData.ship_to_zip]


    #MATH FUNCTIONS FOR INVOICE

    Invoice_Total = sum(Invoice_Total)
    tax_ratio = Decimal(0.05)
    tax = Decimal(Invoice_Total) * tax_ratio
    tax = round(Decimal(tax), 2)
    subtotal = Decimal(tax) + Decimal(Invoice_Total)

    curr_date = str(datetime.today().strftime('%Y-%m-%d'))
    data = {
        'FName': InvoiceData.client.FName,
        'LName': InvoiceData.client.LName,
        'invoice_id': InvoiceData.id,
        'date': curr_date,
        # either ship to or bill to needs to be from the client / the other should have the ability to be edited
        # Right now the shipping info is always from client and billing info is dynamic (either from client or user input)

        'ship_to_name': ShippingInfo[0],
        'ship_to_address': ShippingInfo[1],
        'ship_to_city': ShippingInfo[2],
        'ship_to_state': ShippingInfo[3],
        'ship_to_zip': ShippingInfo[4],

        #assignes billing info to list location from above if statment - Maybe make dict?#####################
        'bill_to_name': BillingInfo[0],
        'bill_to_address': BillingInfo[1],
        'bill_to_city': BillingInfo[2],
        'bill_to_state': BillingInfo[3],
        'bill_to_zip': BillingInfo[4],

        'invoice_all': InvoiceData,
        'line_items': Invoice_Material,
        'Item_Dict': Item_Dict,
        'total': Invoice_Total,
        'tax': tax,
        'subtotal': subtotal,
        'Static_User_Info': Static_User_Info,
    }

    return render(request, 'EmailTemplate.html', data)





#~~~~~~~~~~~~~~~~~~~~~ ADMIN / USER INFO ~~~~~~~~~~~~~~~~~~~~~~~~
def UserInfoView(request):
    User = UserInfo.objects.all()
    for i in User:
        print(i.id)
        U_ID = i.id
    User = UserInfo.objects.get(pk=U_ID)
    UserInfo_Data = UserInfo.objects.get(pk=U_ID)
    initial_data = {
        'ship_to_name': UserInfo_Data.ship_to_name,
        'ship_to_address': UserInfo_Data.ship_to_address,
        'ship_to_city': UserInfo_Data.ship_to_city,
        'ship_to_state': UserInfo_Data.ship_to_state,
        'ship_to_zip': UserInfo_Data.ship_to_zip,
        'email_address': UserInfo_Data.email_address,
        'phone_number': UserInfo_Data.phone_number,
        'markup_value': UserInfo_Data.markup_value,
        'invoice_terms': UserInfo_Data.invoice_terms,
    }


    if request.method == 'POST':
        form = UserInfoForm(request.POST, initial = initial_data, instance = User)
        if form.is_valid():
            messages.success(request, 'Form submission successful')
            form.save()
            return redirect('UserInfo')  # Redirect to the index page after successful submission
    else:
        form = UserInfoForm(instance = User, initial = initial_data)
    return render(request, 'UserInfo.html', {'form': form, 'UserInfo': UserInfo_Data})