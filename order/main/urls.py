from django.urls import path, register_converter
from django.contrib import admin
from main.views import fruitlist_views, orderlist_views, label_views, customer_views
from main.converters import DateConverter

register_converter(DateConverter, 'date')

app_name = 'main'
admin.site.site_header = '아람상회 주문관리'
admin.site.site_title = '아람상회 주문관리'
admin.site.index_title = '회원관리'

urlpatterns = [

    #   과일정보 페이지
    path('', fruitlist_views.index, name='index'),
    path('fruitList/gridlist', fruitlist_views.fruitlist_list,
         name='fruitList_gridlist'),
    path('fruitList/create/', fruitlist_views.fruitlist_create,
         name='fruitlist_create'),
    path('fruitList/modify/',
         fruitlist_views.fruitlist_modify, name='fruitlist_modify'),
    path('fruitList/delete/',
         fruitlist_views.fruitlist_delete, name='fruitlist_delete'),

    #   고객정보 페이지
    path('customerlist/', customer_views.index, name='customer_index'),
    path('customerlist/gridlist', customer_views.customer_list,
         name='customerlist_gridlist'),
    path('customerList/create/', customer_views.customerlist_create,
         name='customerlist_create'),
    path('customerList/modify/',
         customer_views.customerlist_modify, name='customerlist_modify'),
    path('customerList/delete/',
         customer_views.customerlist_delete, name='customerlist_delete'),

    #   주문정보 페이지
    path('orderlist/', orderlist_views.orderlist_index,
         name='orderlist_index'),
    path('orderlist/select/<str:select_date>/', orderlist_views.orderlist_date,
         name='orderlist_date'),
    path('orderlist/create/', orderlist_views.orderlist_create,
         name='orderlist_create'),
    path('orderlist/modifyselect/<int:orderlist_id>/',
         orderlist_views.orderlist_modify_select, name='orderinfo_modify_select'),
    path('orderlist/modify/<int:orderlistModifySelectResult_0_id>/',
         orderlist_views.orderlist_modify, name='orderinfo_modify'),
    path('orderlist/delete/<int:orderlistModifySelectResult_0_id>/',
         orderlist_views.orderlist_delete, name='orderinfo_delete'),

    #     라벨 페이지
    path('label/', label_views.index, name='label_index'),

]
