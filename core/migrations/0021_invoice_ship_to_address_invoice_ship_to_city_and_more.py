# Generated by Django 5.0.2 on 2024-03-23 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_userinfo_invoice_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='ship_to_address',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='ship_to_city',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='ship_to_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='ship_to_state',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='ship_to_zip',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='invoice_terms',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
