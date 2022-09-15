from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from main.models import OrderDetail, OrderInfo


@login_required(login_url='common:login')
def index(request):

    customerListResultQuery = '''
    SELECT 
        moi.id,
        moi.customer_id, 
        mc.customer_name as cn 
    FROM 
        main_orderinfo moi 
            LEFT OUTER JOIN main_customer mc
              ON moi.customer_id = mc.id
            WHERE
                moi.create_date 
                    BETWEEN
                        datetime('now', 'start of day') 
                    AND 
                        datetime('now', 'localtime')
            ORDER BY moi.create_date
    '''

    customerOrderResult = OrderInfo.objects.raw(customerListResultQuery)

    labelListResultQuery = '''
    SELECT 
	    moi.id,
	    mc.customer_name as cn,
	    mf.fruit_name as fn,
	    mf.price as pc,
	    mod.order_quantity as oq, 
	    mod.order_quantity * mf.price as pp, 
	    (SELECT 
            sum(mf2.price * mod2.order_quantity) 
        FROM 
            main_fruitlist mf2
                LEFT OUTER JOIN main_orderdetail as mod2 
                    ON mf2.id = mod2.fruitlist_id 
                LEFT OUTER JOIN main_orderinfo as moi2 
                    ON moi2.id = mod2.orderinfo_id
                LEFT OUTER JOIN main_customer as mc2 
                    ON moi2.customer_id = mc2.id
	    WHERE mod2.create_date 
                BETWEEN 
                    datetime('now', 'start of day') 
                AND 
                    datetime('now', 'localtime') 
                AND
		            moi2.id = moi.id
	    GROUP BY mc2.id) as tp,
        RANK() OVER(PARTITION BY moi.id ORDER BY mod.create_date) as num,
        mod.create_date as cd 
    FROM 
        main_orderdetail as mod
            LEFT OUTER JOIN main_orderinfo as moi 
                ON moi.id = mod.orderinfo_id
            LEFT OUTER JOIN main_customer as mc 
                ON mc.id = moi.customer_id
            LEFT OUTER JOIN main_fruitlist as mf 
                ON mf.id = mod.fruitlist_id
        WHERE 
            mod.create_date 
                BETWEEN 
                    datetime('now', 'start of day') 
                AND 
                    datetime('now', 'localtime')
    '''

    labelListResult = OrderDetail.objects.raw(labelListResultQuery)

    totalPriceResultQuery = '''
        SELECT
            moi2.id, 
            SUM(mod2.order_quantity) as cnt,
            SUM(mf2.price * mod2.order_quantity) as tp
        FROM 
            main_fruitlist mf2
	            LEFT OUTER JOIN main_orderdetail as mod2 
	                ON mf2.id = mod2.fruitlist_id 
	            LEFT OUTER JOIN main_orderinfo as moi2 
                    ON moi2.id = mod2.orderinfo_id
	            LEFT OUTER JOIN main_customer as mc2 
                    ON moi2.customer_id = mc2.id
	        WHERE 
                mod2.create_date 
                    BETWEEN 
                        datetime('now', 'start of day') 
                    AND 
                        datetime('now', 'localtime')
            GROUP BY moi2.id
    '''

    totalPriceResult = OrderDetail.objects.raw(totalPriceResultQuery)

    # if len(labelListResult) < 11:
    #     arg = 11 - len(labelListResult)
    #     for i in range(arg):
    #         labelListResult.append(None)
    # elif len(labelListResult) >= 11
    context = {'labelListResult': labelListResult,
               'customerOrderResult': customerOrderResult,
               'totalPriceResult': totalPriceResult}
    return render(request, 'main/label.html', context)
