from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
import datetime
import json

from main.models import Customer


def customer_list(request):

    customerlist_list = Customer.objects.all().order_by('-create_date')
    tempCustomerList = []

    print('customerlist_list :', customerlist_list)

    for i in range(len(customerlist_list)):
        print('customerlist_list :', customerlist_list[i])
        if(customerlist_list[i] != None):
            tempCustomerList.append(
                customerlist_jsonconvert(customerlist_list[i]))

    customerlist_list = tempCustomerList
    data = {
        "customerlist_list": customerlist_list
    }
    return JsonResponse(data)


def customerlist_jsonconvert(customerlist_list):

    output = {}
    print('customerlist_list.id :', customerlist_list.id)
    print('customerlist_list.customer_name :', customerlist_list.customer_name)
    output["id"] = customerlist_list.id
    output["customer_name"] = customerlist_list.customer_name
    return output


@login_required(login_url='common:login')
def index(request):
    return render(request, 'main/customerlist.html')


@login_required(login_url='common:login')
def customerlist_create(request):
    if request.method == 'POST':
        form = FruitListForm(request.POST)
        if form.is_valid():
            fruitlist = form.save(commit=False)
            fruitlist.author = request.user
            fruitlist.create_date = timezone.now()
            fruitlist.save()

            fruitName = request.POST['fruit_name']
            fn = FruitList.objects.filter(fruit_name=fruitName, create_date__range=[
                datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")])
            fnid = ''
            for i in fn:
                print(i.id)
                fnid = i.id

            query = '''select count(*), orderinfo_id as id from
                (select count(*), orderinfo_id from main_orderdetail mod
                where  fruitlist_id=%s and create_date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime', '+1 Minute') group by orderinfo_id HAVING count(*) != 0
                union all
                select count(*), orderinfo_id from main_orderdetail mod2
                where  fruitlist_id!=%s and create_date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime', '+1 Minute') group by orderinfo_id) A group by orderinfo_id having count(*) = 1'''
            orderDetailResult = OrderDetail.objects.raw(query, [fnid, fnid])
            print(len(orderDetailResult))
            if len(orderDetailResult) > 0:
                print(i)
                for i in orderDetailResult:
                    OrderDetail.objects.create(
                        author=request.user, orderinfo_id=i.id, fruitlist_id=fnid, order_quantity=0)
            return redirect('main:index')
    else:
        form = FruitListForm()
    context = {'form': form}
    return render(request, 'main/fruitlist.html', context)


@csrf_exempt
@login_required(login_url='common:login')
def customerlist_modify(request):
    print('customerlist_modify request : ', request)
    print('customerlist_modify request.body : ', request.body)
    params = json.loads(request.body)
    print('params : ', params)
    print('params["id"] : ', params["id"])
    print('id와 함께온 키값 : ', (list(params.keys()))[1])
    customerUpdateData = Customer.objects.get(id=params["id"])
    customerUpdateData.customer_name = params['customer_name']
    customerUpdateData.save()
    return render(request, 'main/customerlist.html')


@csrf_exempt
@ login_required(login_url='common:login')
def customerlist_delete(request):
    params = json.loads(request.body)
    print('삭제아이디배열 : ', params)
    customerlist = Customer.objects.filter(id__in=params)
    print('삭제할 과일목록 : ', customerlist)
    for i in customerlist:
        print(i.id)
        print(i.customer_name)
    try:
        customerlist.delete()
    except ProtectedError as e:
        print('에러문 : ', e)
        return JsonResponse({'message': '에러가 발생하여 삭제 할 수 없습니다.'})
    return redirect('main:index')
