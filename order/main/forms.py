from django import forms
from main.models import Question, Answer, FruitList, Customer, OrderInfo, OrderDetail


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question  # 사용할모델
        fields = ['subject', 'content']  # QuestionForm에서 사용할 Question모델으 속성
        # widgets = {
        #     'subject': forms.TextInput(attrs={'class': 'form-control'}),
        #     'content': forms.TextInput(attrs={'class': 'form-control', 'rows': 10})
        # }
        labels = {
            'subject': '제목',
            'content': '내용',
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }


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
