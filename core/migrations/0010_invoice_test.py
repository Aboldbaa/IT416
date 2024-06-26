# Generated by Django 5.0.2 on 2024-02-29 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_invoice_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice_Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Proposal', 'Proposal'), ('Open', 'Open'), ('Closed', 'Closed')], default='Draft', max_length=10)),
                ('invoice_number', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
