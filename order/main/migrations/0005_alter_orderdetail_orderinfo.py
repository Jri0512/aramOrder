# Generated by Django 4.0.6 on 2022-09-15 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_answer_create_date_alter_answer_modify_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='orderinfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderinfoidx_orderdetail', to='main.orderinfo'),
        ),
    ]
