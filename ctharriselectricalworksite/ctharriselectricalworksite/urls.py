from django.urls import path
#from . import views
from core import views
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    path('calendar/', views.calendar_page, name='calendar'),

    path('clients/', views.client_list, name='client_list'),    
    path('client/onboarding/', views.client_onboarding_page, name='client_onboarding'),

    path('materials/',views.materials_list, name='materials_list'),
    path('materials/intake/', views.intake_material, name='intake_material'),
    
    path('invoice/', views.invoice_page, name='invoice_page'),
    path('new_invoice/', views.new_invoice, name = 'new_invoice'),
    path('proposal/', views.new_proposal, name='proposal_form'),
    path('create/', views.create_invoice, name='invoice_form'),
    

    path('invoices/', views.invoice_page_form, name='invoice_status'),#Old Maybe But keeping incase it breaks something
    
    
    path('GenPDF/<int:invoice_id>/', views.GenPDF, name='GenPDF'),
    path('pdf_view/', views.ViewPDF.as_view(), name='ViewPDF'),
    path('InvoicePDF/', views.InvoicePDF, name='InvoicePDF'),

    #edit invoice
    path('invoices/edit/<int:invoice_id>/', views.invoice_edit, name='invoice_edit'),
    #~~~~~~~~~~~~~FOR calendar~~~~~~~~~~~~~~~~~~~~~~~~
    path('calendar/', views.calendar_page, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_page, name='calendar_page'),
    # Add other URL patterns as needed
]
