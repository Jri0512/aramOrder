# Generated by Django 4.0.6 on 2022-09-06 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_aramcode_customer_orderinfo_orderdetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]