from django.db import models
import random
import datetime
from django.utils import timezone
import csv

#Testing Formest management in invoice_edit
class test(models.Model):
    name = models.CharField(max_length=100, null=True)
    number = models.CharField(max_length=100, null=True)
    
#End test
class UserInfo(models.Model):
    ship_to_name = models.CharField(max_length=100, null=True)
    
    ship_to_address = models.CharField(max_length=255, null=True)
    ship_to_city = models.CharField(max_length=100, null=True)
    ship_to_state = models.CharField(max_length=100, null=True)
    ship_to_zip = models.CharField(max_length=20, null=True)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    invoice_terms = models.CharField(max_length=20, blank=True)
    markup_value = models.DecimalField(max_digits=4, decimal_places=2)
    def __str__(self):
        return f'{self.id}'
    

class Client(models.Model):
    class Meta: 
        app_label = 'core'     
    FName = models.CharField(max_length=100)
    LName = models.CharField(max_length=100)
    email = models.EmailField()
    contact_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    address_street = models.CharField(max_length=255)
    address_city = models.CharField(max_length=100)
    address_state = models.CharField(max_length=100)
    address_zip = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return self.FName +' '+ self.LName


class Invoice(models.Model):
    class Meta: 
        app_label = 'core' 
    
    DRAFT = 'Draft' #Client only
    PROPOSAL = 'Proposal' #Sent Proposals
    OPEN = 'Open' #Sent Invoice (UnPaid)
    CLOSED = 'Closed' #Sent Invoice (Paid)

    INVOICE_STATUS = (
        (DRAFT, 'Draft'), #Client only
        (PROPOSAL, 'Proposal'), #Sent Proposals
        (OPEN, 'Open'), #Sent Invoice (UnPaid)
        (CLOSED, 'Closed'), #Sent Invoice (Paid)
    )

    status = models.CharField(max_length = 10, choices = INVOICE_STATUS)

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    
    bill_to_name = models.CharField(max_length=100, null=True)
    bill_to_address = models.CharField(max_length=255, null=True)
    bill_to_city = models.CharField(max_length=100, null=True)
    bill_to_state = models.CharField(max_length=100, null=True)
    bill_to_zip = models.CharField(max_length=20, null=True)

    ship_to_name = models.CharField(max_length=100, null=True)
    ship_to_address = models.CharField(max_length=255, null=True)
    ship_to_city = models.CharField(max_length=100, null=True)
    ship_to_state = models.CharField(max_length=100, null=True)
    ship_to_zip = models.CharField(max_length=20, null=True)


    balance_due = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    line_items = models.ManyToManyField(to='Material', through='InvoiceMaterial') #custom through model

#    def save(self, *args, **kwargs):
#        # Calculate subtotal
#        self.subtotal = sum(item.amount for item in self.item_set.all())
#        
#        # Calculate tax (0.25% of subtotal)
#        self.tax = self.subtotal * 0.0025
#       
#       # Calculate total
#       self.total = self.subtotal + self.tax
#        
#        # Set balance due
#        self.balance_due = self.total
#        
#        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.id} - ({self.client})"

class Material(models.Model):
    item = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item

#This establishes many to many relationship between Invoice and Material
class InvoiceMaterial(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    markup = models.BooleanField(default=0)
    #item = models.CharField(max_length=100, default=1) #required for migration(DNRemove)
    #price = models.DecimalField(max_digits=10, decimal_places=2, default=0) #required for migration(DNRemove)

    @property
    def total_price(self):
        return self.quantity * self.material.price
    
    class Meta:
        unique_together = ('invoice', 'material')

    def __str__(self):
        return f" {self.invoice.id} {self.invoice.client} {self.material} ({self.quantity})"