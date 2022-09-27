from django.urls import path
from django.contrib import admin
from main.views import fruitlist_views, orderlist_views, label_views

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

    #   주문정보 페이지
    path('orderlist/', orderlist_views.orderlist_index,
         name='orderlist_index'),
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
