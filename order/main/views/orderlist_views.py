from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.dateformat import DateFormat

from main.models import FruitList, OrderDetail, Customer, OrderInfo, User
from main.forms import CustomerForm

import datetime


@login_required(login_url='common:login')
def orderlist_index(request):

    # startDate = DateFormat(
    #     datetime.datetime.now()).format('Y-m-d 00:00:00')
    # endDate = DateFormat(
    #     datetime.datetime.now()).format('Y-m-d 23:59:59')
    selectDate = DateFormat(
        datetime.datetime.now()).format('Y-m-d')

    userInfo = user_group_check(request.user.id)
    storePlace = userInfo[0].gname

    fruitlist_list = fruitlist_quantity_select(selectDate)
    orderlistResult = orderlist_select(selectDate, request)
    context = {'fruitlist_list': fruitlist_list,
               'orderlistResult': orderlistResult,
               'storePlace': storePlace}
    for i, e in enumerate(orderlistResult):
        if len(fruitlist_list) != len(e.oq):
            loopRangeNum = len(fruitlist_list) - len(e.oq)
            for i in range(loopRangeNum):
                e.oq.append(0)
    return render(request, 'main/orderlist.html', context)


def orderlist_date(request, select_date):
    # 일자 정보 변환
    userInfo = user_group_check(request.user.id)
    storePlace = userInfo[0].gname
    fruitlist_list = fruitlist_quantity_select(select_date)
    orderlistResult = orderlist_select(select_date, request)
    context = {'fruitlist_list': fruitlist_list,
               'orderlistResult': orderlistResult,
               'orderDate': select_date,
               'storePlace': storePlace}
    for i, e in enumerate(orderlistResult):
        if len(fruitlist_list) != len(e.oq):
            loopRangeNum = len(fruitlist_list) - len(e.oq)
            for i in range(loopRangeNum):
                e.oq.append(0)
    return render(request, 'main/orderlist.html', context)

# 과일명 및 총수량+재고수량


def fruitlist_quantity_select(selectDate):

    startDate = selectDate + ' 00:00:00'
    endDate = selectDate + ' 23:59:59'

    query = '''select mf.id, mf.fruit_name, mf.quantity, mf.price, IFNULL(SUM(mod.order_quantity),0) as oq, IFNULL((mf.quantity - sum(mod.order_quantity)),mf.quantity) as stock ,  mf.create_date from main_fruitlist as mf
            left outer join main_orderdetail as mod
            on mf.id = mod.fruitlist_id
			where mf.create_date BETWEEN %s AND %s
			group by mf.id'''

    fruitQuantityResult = FruitList.objects.raw(query, [startDate, endDate])
    return fruitQuantityResult

# 고객별 주문내역


def orderlist_select(selectDate, request):

    startDate = selectDate + ' 00:00:00'
    endDate = selectDate + ' 23:59:59'
    userInfo = user_group_check(request.user.id)
    groupId = userInfo[0].gid

    query = '''select moi.id, mc.customer_name as cn, group_concat(IFNULL(mod.order_quantity,0),',') as oq, sum(mod.order_quantity * mf.price) as tp, mod.create_date as cd, ma.name as pmn, ma2.name as stn from main_orderdetail as mod
            left outer join main_orderinfo as moi on moi.id = mod.orderinfo_id
            left outer join main_customer as mc on mc.id = moi.customer_id
            left outer join main_fruitlist as mf on mf.id = mod.fruitlist_id
			left outer join main_aramcode as ma on ma.id = moi.payment_method_id
			left outer join main_aramcode as ma2 on ma2.id = moi.shipping_type_id
			where (mod.create_date BETWEEN %s AND %s) and moi.store_place_id = %s
            group by mc.customer_name'''

    orderListResult = OrderDetail.objects.raw(
        query, [startDate, endDate, groupId])
    for i, e in enumerate(orderListResult):
        temp = []
        oqArr = (e.oq).split(',')
        for j in oqArr:
            temp.append(j)
        e.oq = temp
    return orderListResult


@ login_required(login_url='common:login')
def orderlist_create(request):

    selectDate = DateFormat(
        datetime.datetime.now()).format('Y-m-d')

    fruitlist_list = FruitList.objects.filter(create_date__range=[
        datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).values()

    customerIdCheck = None
    orderInfoIdCheck = None
    customerId = None
    orderInfoId = None
    # print('request.user : ', request.user)
    # userName = str(request.user)
    userGroupIdCheck = user_group_check(request.user.id)
    storePlace = userGroupIdCheck[0].gname

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
                author=request.user, customer_id=customerId, payment_method_id=request.POST['payment_method'], shipping_type_id=request.POST['shipping_type'], store_place_id=userGroupIdCheck[0].gid)
        # OrderInfoId 조회
        orderInfoIdCheck = OrderInfo.objects.filter(customer_id=customerId, create_date__range=[
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).values()
        orderInfoId = orderInfoIdCheck[0]['id']
        fruitQuantityCheck = fruitlist_quantity_select(selectDate)
        fruitQuantityCheckFlag = False

        for i in range(len(fruitlist_list)):
            if(fruitlist_list[i] != None):
                fruit_id = fruitlist_list[i]['id']
                quantity = (
                    request.POST[fruitlist_list[i]['fruit_name']]).strip()
                try:
                    if quantity != '':
                        OrderDetail.objects.create(
                            author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=quantity)
                    elif quantity == '':
                        OrderDetail.objects.create(
                            author=request.user, orderinfo_id=orderInfoId, fruitlist_id=fruit_id, order_quantity=0)
                    elif fruitQuantityCheck[i]['stock'] - quantity <= 0:
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

    context = {'fruitlist_list': fruitlist_quantity_select(selectDate),
               'orderlistResult': orderlist_select(selectDate, request),
               'validationError': validationError,
               'storePlace': storePlace}
    return render(request, 'main/orderlist.html', context)


def user_group_check(userId):
    query = '''
        select au.id, au.username as name, ag.id as gid, ag.name as gname from auth_user au
        left outer join auth_user_groups aug
        on au.id = aug.user_id
        left outer join auth_group ag
        on aug.group_id = ag.id
        where au.id = %s
        '''
    userGroup = User.objects.raw(query, [userId])
    return userGroup


@ login_required(login_url='common:login')
def orderlist_modify_select(request, orderlist_id):
    query = '''
        select moi.id, moi.create_date as moicd, mod.id as modid, mc.customer_name as cn, mf.fruit_name as fn, mf.id as mfid, mod.fruitlist_id as fid, mod.order_quantity as qn, moi.payment_method_id as pmi, ma.name as pmn, moi.shipping_type_id as sti, ma2.name as stin from main_orderinfo moi
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
        where moi.id = %s
        group by mf.id'''

    orderlistModifySelectResult = OrderDetail.objects.raw(query, [
        orderlist_id])
    if len(orderlistModifySelectResult) > 0:
        selectDate = orderlistModifySelectResult[0].moicd.strftime('%Y-%m-%d')
    else:
        return redirect('main:orderlist_index')
    fruitlist_list = fruitlist_quantity_select(selectDate)
    orderlistResult = orderlist_select(selectDate, request)
    for i, e in enumerate(orderlistResult):
        if len(fruitlist_list) != len(e.oq):
            loopRangeNum = len(fruitlist_list) - len(e.oq)
            for i in range(loopRangeNum):
                e.oq.append(0)

    userInfo = user_group_check(request.user.id)
    storePlace = userInfo[0].gname
    context = {'fruitlist_list': fruitlist_list,
               'orderlistResult': orderlistResult,
               'orderlistModifySelectResult': orderlistModifySelectResult,
               'storePlace': storePlace
               }
    return render(request, 'main/orderlist.html', context)


@ login_required(login_url='common:login')
def orderlist_modify(request, orderlistModifySelectResult_0_id):
    values = request.POST.dict()
    updateIdList = []
    updateValueList = []
    fruitQuantityCheckFlag = False
    orderDate = OrderInfo.objects.get(id=orderlistModifySelectResult_0_id)
    selectDate = orderDate.create_date.strftime('%Y-%m-%d')
    fruitQuantityCheck = fruitlist_quantity_select(selectDate)
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
    userInfo = user_group_check(request.user.id)
    storePlace = userInfo[0].gname
    context = {'fruitlist_list': fruitlist_quantity_select(selectDate),
               'orderlistResult': orderlist_select(selectDate, request),
               'validationError': validationError,
               'storePlace': storePlace}
    return render(request, 'main/orderlist.html', context)


@ csrf_exempt
@ login_required(login_url='common:login')
def orderlist_delete(request, orderlistModifySelectResult_0_id):
    orderInfo = OrderInfo.objects.get(id=orderlistModifySelectResult_0_id)
    selectDate = orderInfo.create_date.strftime('%Y-%m-%d')
    orderInfo.delete()
    context = {'fruitlist_list': fruitlist_quantity_select(selectDate),
               'orderlistResult': orderlist_select(selectDate, request),
               }
    return render(request, 'main/orderlist.html', context)
