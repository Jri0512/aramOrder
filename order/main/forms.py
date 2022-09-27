from django import forms
from main.models import FruitList, Customer, OrderInfo, OrderDetail


class FruitListForm(forms.ModelForm):
    class Meta:
        model = FruitList
        fields = ['fruit_name', 'price', 'quantity']

        labels = {
            'fruit_name': '과일명',
            'price': '가격',
            'quantity': '수량',
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name']

        labels = {
            'customer_name': '고객명',
        }


class OrderInfoForm(forms.ModelForm):
    class Meta:
        model = OrderInfo
        fields = ['customer']

        labels = {
            'customer': '고객명',
        }


class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = OrderDetail
        fields = ['order_quantity', 'fruitlist', 'orderinfo']

        labels = {
            'order_quantity': '주문수량',
        }
