from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from django.db.models.deletion import ProtectedError
from main.forms import FruitListForm
from main.models import FruitList, OrderDetail
import datetime
import json


def fruitlist_list(request):
    # fruitlist_list = serializers.serialize(
    #     "json", FruitList.objects.order_by('-create_date'))
    # fruitlist_data = {
    #     "result": fruitlist_list
    # }

    fruitlist_list = FruitList.objects.filter(create_date__range=[
        datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"), datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")]).order_by('-create_date')
    tempFruitList = []

    for i in range(len(fruitlist_list)):
        if(fruitlist_list[i] != None):
            tempFruitList.append(fruitlist_jsonconvert(fruitlist_list[i]))

    fruitlist_list = tempFruitList
    data = {
        "fruitlist_list": fruitlist_list
    }
    return JsonResponse(data)


def fruitlist_jsonconvert(fruitlist):

    output = {}
    output["id"] = fruitlist.id
    output["author_id"] = fruitlist.author_id
    output["fruit_name"] = fruitlist.fruit_name
    output["price"] = fruitlist.price
    output["quantity"] = fruitlist.quantity
    return output


@login_required(login_url='common:login')
def index(request):
    return render(request, 'main/fruitlist.html')


@login_required(login_url='common:login')
def fruitlist_create(request):
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
def fruitlist_modify(request):
    print('fruitlist_modify request : ', request)
    print('fruitlist_modify request.body : ', request.body)
    params = json.loads(request.body)
    print('params : ', params)
    print('params["id"] : ', params["id"])
    print('id와 함께온 키값 : ', (list(params.keys()))[1])
    fruitUpdateData = FruitList.objects.get(id=params["id"])
    fruitUpdateData.fruit_name = params['fruit_name']
    fruitUpdateData.price = params['price']
    fruitUpdateData.quantity = params['quantity']
    fruitUpdateData.save()
    return render(request, 'main/fruitlist.html')


@csrf_exempt
@ login_required(login_url='common:login')
def fruitlist_delete(request):
    params = json.loads(request.body)
    print('삭제아이디배열 : ', params)
    fruitlist = FruitList.objects.filter(id__in=params)
    print('삭제할 과일목록 : ', fruitlist)
    for i in fruitlist:
        print(i.id)
        print(i.fruit_name)
        print(i.price)
        print(i.quantity)
    try:
        fruitlist.delete()
    except ProtectedError as e:
        print('에러문 : ', e)
        return JsonResponse({'message': '해당 과일의 주문내역이 존재하여 삭제 할 수 없습니다.'})
    return redirect('main:index')
