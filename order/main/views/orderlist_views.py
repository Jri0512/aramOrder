from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.utils import timezone

from main.models import FruitList, OrderDetail, Customer, OrderInfo
from main.forms import CustomerForm

import datetime


@login_required(login_url='common:login')
def orderlist_index(request):
    fruitlist_list = fruitlist_quantity_select(request)
    orderlistResult = orderlist_select(request)
    context = {'fruitlist_list': fruitlist_list,
               'orderlistResult': orderlistResult}
    for i, e in enumerate(orderlistResult):
        if len(fruitlist_list) != len(e.oq):
            loopRangeNum = len(fruitlist_list) - len(e.oq)
            for i in range(loopRangeNum):
                e.oq.append(0)
    return render(request, 'main/orderlist.html', context)

# 과일명 및 총수량+재고수량


@login_required(login_url='common:login')
def fruitlist_quantity_select(request):
    query = '''select mf.id, mf.fruit_name, mf.quantity, mf.price, IFNULL(SUM(mod.order_quantity),0) as oq, IFNULL((mf.quantity - sum(mod.order_quantity)),mf.quantity) as stock ,  mf.create_date from main_fruitlist as mf
            left outer join main_orderdetail as mod
            on mf.id = mod.fruitlist_id
			where mf.create_date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime', '+1 Minute')
			group by mf.id'''

    fruitQuantityResult = FruitList.objects.raw(query)
    return fruitQuantityResult

# 고객별 주문내역


@login_required(login_url='common:login')
def orderlist_select(requst):
    query = '''select moi.id, mc.customer_name as cn, group_concat(IFNULL(mod.order_quantity,0),',') as oq, sum(mod.order_quantity * mf.price) as tp, mod.create_date as cd, ma.name as pmn, ma2.name as stn from main_orderdetail as mod
            left outer join main_orderinfo as moi on moi.id = mod.orderinfo_id
            left outer join main_customer as mc on mc.id = moi.customer_id
            left outer join main_fruitlist as mf on mf.id = mod.fruitlist_id
			left outer join main_aramcode as ma on ma.id = moi.payment_method_id
			left outer join main_aramcode as ma2 on ma2.id = moi.shipping_type_id
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
def orderlist_create(request):
    fruitlist_list = FruitList.objects.filter(create_date__range=[
        datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).values()

    customerIdCheck = None
    orderInfoIdCheck = None
    customerId = None
    orderInfoId = None
    if request.method == 'POST':
        customerName = request.POST['customer_name']

        # 고객명 유효성 검사 하여 생성
        customerIdCheck = Customer.objects.filter(
            customer_name=customerName).exists()
        if customerIdCheck == False:
            form = CustomerForm(request.POST)
            if form.is_valid():
                customer = form.save(commit=False)
                customer.author = request.user
                customer.save()
        # 고객Id 조회
        customerIdCheck = Customer.objects.filter(
            customer_name=customerName).values()
        customerId = customerIdCheck[0]['id']

        # OrderInfo를 검사 하여 생성
        orderInfoIdCheck = OrderInfo.objects.filter(customer_id=customerId, create_date__range=[
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).exists()
        if orderInfoIdCheck == False:
            OrderInfo.objects.create(
                author=request.user, customer_id=customerId, payment_method_id=request.POST['payment_method'], shipping_type_id=request.POST['shipping_type'])
        # OrderInfoId 조회
        orderInfoIdCheck = OrderInfo.objects.filter(customer_id=customerId, create_date__range=[
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).values()
        orderInfoId = orderInfoIdCheck[0]['id']
        fruitQuantityCheck = fruitlist_quantity_select(request)
        fruitQuantityCheckFlag = False

        for i in range(len(fruitlist_list)):
            if(fruitlist_list[i] != None):
                fruit_id = fruitlist_list[i]['id']
                quantity = (
                    request.POST[fruitlist_list[i]['fruit_name']]).strip()
                print('quantity : ', quantity)
                print('quantity == '' : ', quantity == '')
                print('orderInfoIdCheck : ', orderInfoIdCheck)
                print('orderInfoId 체크 : ', orderInfoId)
                try:
                    if quantity != '':
                        print('3번 if문 : ', quantity)
                        OrderDetail.objects.create(
                            author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=quantity)
                    elif quantity == '':
                        print('1번 if문 : ', quantity)
                        OrderDetail.objects.create(
                            author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=0)
                    elif fruitQuantityCheck[i]['stock'] - quantity <= 0:
                        print('2번 if문 : ', quantity)
                        OrderDetail.objects.create(
                            author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=0)
                        fruitQuantityCheckFlag = True
                    validationError = '주문 입력 완료'
                except:
                    rollbackOrderInfo = OrderInfo.objects.get(id=orderInfoId)
                    rollbackOrderInfo.delete()
                    validationError = '수량을 숫자로 입력해주세요'
        if fruitQuantityCheckFlag == True:
            validationError = '재고 부족 항목 주문 실패'
    context = {'fruitlist_list': fruitlist_quantity_select(request),
               'orderlistResult': orderlist_select(request),
               'validationError': validationError}
    return render(request, 'main/orderlist.html', context)


@login_required(login_url='common:login')
def orderlist_modify_select(request, orderlist_id):
    query = '''
        select moi.id, mod.id as modid, mc.customer_name as cn, mf.fruit_name as fn, mf.id as mfid, mod.fruitlist_id as fid, mod.order_quantity as qn, moi.payment_method_id as pmi, ma.name as pmn, moi.shipping_type_id as sti, ma2.name as stin from main_orderinfo moi
        left outer join main_orderdetail mod
        on moi.id = mod.orderinfo_id
		left outer join main_fruitlist mf
        on mod.fruitlist_id = mf.id
        left outer join main_customer mc
        on moi.customer_id = mc.id
		left outer join main_aramcode ma
		on moi.payment_method_id = ma.id
		left outer join main_aramcode ma2
		on moi.shipping_type_id = ma2.id
        where moi.id = %s and mf.create_date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime', '+1 Minute')
        group by mf.id'''

    orderlistModifySelectResult = OrderDetail.objects.raw(query, [
                                                          orderlist_id])
    fruitlist_list = fruitlist_quantity_select(request)
    orderlistResult = orderlist_select(request)
    for i, e in enumerate(orderlistResult):
        if len(fruitlist_list) != len(e.oq):
            loopRangeNum = len(fruitlist_list) - len(e.oq)
            for i in range(loopRangeNum):
                e.oq.append(0)

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
    fruitQuantityCheckFlag = False
    fruitQuantityCheck = fruitlist_quantity_select(request)
    for i in values:
        if i != 'csrfmiddlewaretoken' and i != 'customer_name':
            updateIdList.append(i)
            updateValueList.append(values[i])
    modifyOrderMethodList = OrderInfo.objects.get(
        id=orderlistModifySelectResult_0_id)

    modifyOrderMethodList.payment_method_id = request.POST['payment_method']
    modifyOrderMethodList.shipping_type_id = request.POST['shipping_type']
    modifyOrderMethodList.save()

    modifyOrderFruitList = OrderDetail.objects.filter(
        orderinfo_id=orderlistModifySelectResult_0_id).order_by('id')
    idx = 0
    try:
        for detail in modifyOrderFruitList:
            if str(detail.fruitlist_id) == updateIdList[idx] and str(detail.order_quantity) != updateValueList[idx]:
                if (int(fruitQuantityCheck[idx].stock) + int(detail.order_quantity)) - int(updateValueList[idx]) < 0:
                    fruitQuantityCheckFlag = True
                elif (int(fruitQuantityCheck[idx].stock) + int(detail.order_quantity)) - int(updateValueList[idx]) >= 0:
                    detail.order_quantity = int(updateValueList[idx])
                    detail.modify_date = timezone.now()
                    detail.save()
            idx += 1
        validationError = '수정 완료'
    except:
        validationError = '수량을 숫자로 입력해주세요'
    if fruitQuantityCheckFlag == True:
        validationError = ' - 재고 부족 항목 주문 실패'

    context = {'fruitlist_list': fruitlist_quantity_select(request),
               'orderlistResult': orderlist_select(request),
               'validationError': validationError}
    return render(request, 'main/orderlist.html', context)


@csrf_exempt
@ login_required(login_url='common:login')
def orderlist_delete(request, orderlistModifySelectResult_0_id):
    orderInfo = OrderInfo.objects.get(id=orderlistModifySelectResult_0_id)
    orderInfo.delete()
    return redirect('main:orderlist_index')
