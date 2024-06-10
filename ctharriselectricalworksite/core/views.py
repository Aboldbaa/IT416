from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, Material, Invoice, InvoiceMaterial 
from django.db.models import Q

from .forms import ClientOnboardingForm, ClientForm, InvoiceForm, MaterialForm, NewInvoice_EmptyForm, InvoiceMaterialFormSet
    
from django.utils import timezone
from django.urls import reverse
from datetime import date, timedelta
import calendar
import time

#PDF GENERATION IMPORTS
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa







#Homepage - Invoice Table
def ClientInfo(request):
    clients = Client.objects.all()
    return render(request, 'index.html', {'user': clients})
#Invoice page 

def invoice_page(request):
    invoice = Invoice.objects.all()
    return render(request, 'invoice.html', {'invoices': invoice})

#materials page 
#general view for requesting materials
def materials_list(request):
    materials = Material.objects.all()
    return render(request, 'materials.html', {'materials': materials})

#to save material to database
def intake_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('materials_list')
    else:
        form = MaterialForm()
    return render(request, 'materialsintakeform.html', {'form': form})

#Search function for material
def materials_list(request):
    search_query = request.GET.get('search')

    if search_query:
        materials = Material.objects.filter(
            Q(item__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(price__icontains=search_query)
        )
    else:
        materials = Material.objects.all()

    return render(request, 'materials.html', {'materials': materials})


#Client
# Retrieve all invoices from the database and pass them to the index template
def index(request):
    invoice = Invoice.objects.all()
    return render(request, 'index.html', {'invoices': invoice})

# Retrieve all clients from the database and pass them to the client template
def client_list(request):
    clients = Client.objects.all()
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

# Calendar view
def calendar_page(request, year=None, month=None):
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
            week_list.append(day.day if day.month == month else '')
        month_calendar.append(week_list)

    return month_calendar

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~END CALENDAR~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#proposal page
def proposal_form(request):
    # Your logic for handling form submission and rendering the template goes here
    # For now, let's just render the template without any additional context data
    return render(request, 'proposalform.html')





#New Invoice Page
def new_invoice(request):
    if request.method == 'POST':
        Invoice_Form = InvoiceForm(request.POST)

        ClientOnboarding_Form = ClientOnboardingForm(request.POST)

        if ClientOnboarding_Form.is_valid():
            ClientOnboarding_Form.save()
            return redirect('/new_invoice')  # Redirect to the index page after successful submission
        
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


    return render(request, 'new_invoice.html', {'NewCustomer': ClientOnboarding_Form, 'Invoice_Form': Invoice_Form, 'Invoice_FormSet': Invoice_FormSet})






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
                formset.save()
                return redirect('index')
    else:
        form = InvoiceForm()
        formset = InvoiceMaterialFormSet()
    return render(request, 'invoice_form.html', {'form': form, 'formset': formset})

#~~~~~~~~~~~~~~~~~~~~~EDITING INVOICE~~~~~~~~~~~~~~~~~~~~~~~~
def invoice_edit(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceMaterialFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('invoice_list') # Or wherever you wish to redirect
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceMaterialFormSet(instance=invoice)
    return render(request, 'invoice_edit.html', {'form': form, 'formset': formset, 'invoice': invoice})






#~~~~~~~~~~~~~~~~~~~~~PDF GENERATION THINGS~~~~~~~~~~~~~~~~~~~~~~~~
def GenPDF(request, invoice_id):
    buffer = io.BytesIO()
    print(type(invoice_id))
    c = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 12)

#Generate content for pdf - - OLD
    # Generate content for pdf

    SpecificInvoice = Invoice.objects.get(pk=invoice_id)
    #Material = InvoiceMaterial.objects.get(pk=invoice_id)

    ReqInfo = ['client', 'amount', 'date', 'terms', 'bill_to_name', 'bill_to_address', 'ship_to_name', 'ship_to_address', 'quantities', 'price', 'item_description', 'line_items']

    lines = []

    # adding items to list

    ClientName = SpecificInvoice.client.FName + " " + SpecificInvoice.client.LName
    lines.append(ClientName)





    for item in SpecificInvoice.line_items.all():
        combined = "Item: " + str(item.item) + "   " + "Price: " + str(item.price) #converts item to string (To add to list, otherwise = error :( )
        lines.append(combined)
        
        


    CurrentDate = time.strftime("%Y-%m-%d") #Specifically for the file name


#Display content on pdf
    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=str(invoice_id) + '_' + ClientName + '_' + CurrentDate + '.pdf')



#~~~~~~~~~~~~~~~~~~~~~END PDF GENERATION~~~~~~~~~~~~~~~~~~~~~~~~



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

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class ViewPDF(View):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('InvoicePDF.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    

def InvoicePDF(request):
    invoice_id = '9' #This is a test value
    invoice = Invoice.objects.get(pk=invoice_id)
    return render(request, 'InvoicePDF.html', {'customer':invoice})


#~~~~~~~~~~~~~~~~~~~~~ END NEW PDF GENERATION ~~~~~~~~~~~~~~~~~~~~~~~~