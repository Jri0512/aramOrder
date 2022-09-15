from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect

from main.models import FruitList, OrderDetail, Customer, OrderInfo
from main.forms import CustomerForm

import datetime


@login_required(login_url='common:login')
def orderlist_index(request):
    fruitlist_list = fruitlist_quantity_select(request)
    orderlistResult = orderlist_select(request)
    context = {'fruitlist_list': fruitlist_list,
               'orderlistResult': orderlistResult}
    print('orderlistResult : ', orderlistResult)
    for i, e in enumerate(orderlistResult):
        print(i, '번째 값 : ', e.id, e.cn, e.oq, e.tp, e.cd)
    return render(request, 'main/orderlist.html', context)


@login_required(login_url='common:login')
def orderlist_create(request):
    fruitlist_list = FruitList.objects.filter(create_date__range=[
        datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).order_by('-create_date').values()

    customerIdCheck = None
    orderInfoIdCheck = None
    customerId = None
    orderInfoId = None

    if request.method == 'POST':
        customerName = request.POST['customer_name']

        # 고객명 유효성 검사 하여 생성
        customerIdCheck = Customer.objects.filter(
            customer_name=customerName).exists()
        print('1 :', customerIdCheck)
        if customerIdCheck == False:
            form = CustomerForm(request.POST)
            if form.is_valid():
                customer = form.save(commit=False)
                customer.author = request.user
                customer.save()
        # 고객Id 조회
        customerIdCheck = Customer.objects.filter(
            customer_name=customerName).values()
        print('2 :', customerIdCheck)
        customerId = customerIdCheck[0]['id']

        # OrderInfo를 검사 하여 생성
        orderInfoIdCheck = OrderInfo.objects.filter(customer_id=customerId, create_date__range=[
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).exists()
        if orderInfoIdCheck == False:
            OrderInfo.objects.create(
                author=request.user, customer_id=customerId, payment_method_id=1, shipping_type_id=3)
        # OrderInfoId 조회
        orderInfoIdCheck = OrderInfo.objects.filter(customer_id=customerId, create_date__range=[
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).values()
        orderInfoId = orderInfoIdCheck[0]['id']

        for i in range(len(fruitlist_list)):
            if(fruitlist_list[i] != None):
                fruit_id = fruitlist_list[i]['id']
                quantity = request.POST[fruitlist_list[i]['fruit_name']]
                if quantity != '':
                    OrderDetail.objects.create(
                        author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=quantity)
                elif quantity == '':
                    OrderDetail.objects.create(
                        author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=0)

    hi = OrderDetail.objects.all()
    for i in hi:
        print(i)

    return render(request, 'main/orderlist.html', context={'fruitlist_list': fruitlist_quantity_select(request),
                                                           'orderlistResult': orderlist_select(request)})


@login_required(login_url='common:login')
def orderlist_select(requst):
    query = '''select moi.id, mc.customer_name as cn, group_concat(mod.order_quantity,',') as oq, sum(mod.order_quantity * mf.price) as tp, mod.create_date as cd from main_orderdetail as mod
            left outer join main_orderinfo as moi on moi.id = mod.orderinfo_id
            left outer join main_customer as mc on mc.id = moi.customer_id
            left outer join main_fruitlist as mf on mf.id = mod.fruitlist_id
			where mod.create_date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime', '+1 Minute')
            group by mc.customer_name'''

    orderListResult = OrderDetail.objects.raw(query)
    for i, e in enumerate(orderListResult):
        temp = []
        oqArr = (e.oq).split(',')
        for j in oqArr:
            temp.append(j)
        e.oq = temp
    return orderListResult


@login_required(login_url='common:login')
def fruitlist_quantity_select(request):
    query = '''select mf.id, mf.fruit_name, mf.quantity, IFNULL(SUM(mod.order_quantity),0) as oq, IFNULL((mf.quantity - sum(mod.order_quantity)),0) as stock ,  mf.create_date from main_fruitlist as mf
            left outer join main_orderdetail as mod
            on mf.id = mod.fruitlist_id
			where mf.create_date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime')
			group by mf.id'''

    fruitQuantityResult = FruitList.objects.raw(query)
    return fruitQuantityResult


@login_required(login_url='common:login')
def orderlist_modify_select(request, orderlist_id):
    query = '''
        select moi.id, mod.id as modid, mc.customer_name as cn, mf.fruit_name as fn, mod.fruitlist_id as fid, mod.order_quantity as qn from main_orderdetail mod
        left outer join main_orderinfo moi
        on mod.orderinfo_id = moi.id
        left outer join main_customer mc
        on moi.customer_id = mc.id
        left outer join main_fruitlist mf
        on mod.fruitlist_id = mf.id
        where moi.id = %s'''

    orderlistModifySelectResult = OrderDetail.objects.raw(query, [
                                                          orderlist_id])
    fruitlist_list = fruitlist_quantity_select(request)
    orderlistResult = orderlist_select(request)
    context = {'fruitlist_list': fruitlist_list,
               'orderlistResult': orderlistResult,
               'orderlistModifySelectResult': orderlistModifySelectResult
               }
    return render(request, 'main/orderlist.html', context)


@ login_required(login_url='common:login')
def orderlist_modify(request, orderlistModifySelectResult_0_id):
    values = request.POST.dict()
    updateIdList = []
    updateValueList = []
    for i in values:
        if i != 'csrfmiddlewaretoken' and i != 'customer_name':
            updateIdList.append(i)
            updateValueList.append(values[i])

    orderDetailList = OrderDetail.objects.filter(id__in=updateIdList)
    idx = 0
    for i in orderDetailList:
        i.order_quantity = updateValueList[idx]
        i.save()
        idx += 1
    idx = None

    return redirect('main:orderlist_index')


@csrf_exempt
@ login_required(login_url='common:login')
def orderlist_delete(request, orderlistModifySelectResult_0_id):
    orderInfo = OrderInfo.objects.get(id=orderlistModifySelectResult_0_id)
    orderInfo.delete()
    return redirect('main:orderlist_index')
