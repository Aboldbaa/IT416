from django.urls import path
#from . import views
from core import views
from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('UserInfo/', views.UserInfoView, name='UserInfo'),

    path('', views.index, name='index'),
    path('calendar/', views.calendar_page, name='calendar'),

    path('clients/', views.client_list, name='client_list'),    
    path('client/onboarding/', views.client_onboarding_page, name='client_onboarding'),
     path('clients/<int:client_id>/edit/', views.client_edit, name='client_edit'),

    path('materials/',views.materials_list, name='materials_list'),
    path('materials/<int:material_id>/edit/', views.materials_edit, name='materials_edit'),
    path('materials/intake/', views.intake_material, name='intake_material'),
    
    path('invoice/', views.invoice_page, name='invoice_page'),
    path('invoice/change-status/<int:invoice_id>/', views.invoice_change_status, name='invoice_change_status'),
    path('new_invoice/', views.new_invoice, name = 'new_invoice'),
    path('proposal/', views.new_proposal, name='proposal_form'),
    path('create/', views.create_invoice, name='invoice_form'),
    #path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/search/', views.invoice_search, name='invoice_search'),
    

    path('invoices/', views.invoice_page_form, name='invoice_status'),#Old Maybe But keeping incase it breaks something
    
    
    path('pdf_view/<int:invoice_id>/', views.ViewPDF.as_view(), name='ViewPDF'),
    path('InvoicePDF/', views.InvoicePDF, name='InvoicePDF'),


    path('InvoiceFinalize/<int:invoice_id>/', views.InvoiceFinalize, name='InvoiceFinalize'), #Used to get PDF and send email to client Better Name FinalizeInvoice
    path('EmailTemplate/', views.EmailTemplate, name='EmailTemplate'),

    #edit invoice
    path('invoices/edit/<int:invoice_id>/', views.invoice_edit, name='invoice_edit'),
    
    #delete invoice
    path('invoices/delete/<int:invoice_id>/', views.invoice_delete, name='invoice_delete'),

    # URL pattern for dynamically deleting an InvoiceMaterial item via HTMX
    path('invoice-material/<int:item_id>/delete/', views.invoice_material_delete, name='invoice_material_delete'),
    #~~~~~~~~~~~~~FOR calendar~~~~~~~~~~~~~~~~~~~~~~~~
    path('calendar/', views.calendar_page, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_page, name='calendar_page'),
    # Add other URL patterns as needed
]