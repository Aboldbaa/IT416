# Generated by Django 5.0.2 on 2024-03-27 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_invoice_bill_to_city_invoice_bill_to_state_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('number', models.CharField(max_length=100, null=True)),
            ],
        ),
    ]
