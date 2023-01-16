from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.


class FruitList(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='author_fruitList')
    fruit_name = models.CharField(max_length=100)
    price = models.IntegerField()
    quantity = models.IntegerField()
    create_date = models.DateTimeField(auto_now=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)


class Customer(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='author_customer')
    customer_name = models.CharField(unique=True, max_length=100)
    create_date = models.DateTimeField(auto_now=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)


class AramCode(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='author_aramCode')
    name = models.CharField(null=False, max_length=100)
    create_date = models.DateTimeField(auto_now=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)


class OrderInfo(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='author_orderInfo')
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='customer_orderinfo')
    payment_method = models.ForeignKey(
        AramCode, on_delete=models.PROTECT, related_name='payment_orderinfo')
    shipping_type = models.ForeignKey(
        AramCode, on_delete=models.PROTECT, related_name='shipping_orderinfo')
    store_place = models.ForeignKey(
        Group, on_delete=models.PROTECT, related_name='store_orderinfo', default=1)
    create_date = models.DateTimeField(auto_now=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)


class OrderDetail(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='author_orderDetail')
    orderinfo = models.ForeignKey(
        OrderInfo, on_delete=models.CASCADE, related_name='orderinfoidx_orderdetail')
    fruitlist = models.ForeignKey(
        FruitList, on_delete=models.PROTECT, related_name='fruitidx_orderdetail')
    order_quantity = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)
