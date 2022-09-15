from django.urls import path
from main.views import base_views, answer_views, question_views, fruitlist_views, orderlist_views, label_views

app_name = 'main'

urlpatterns = [
    # path('', base_views.index, name='index'),
    path('<int:question_id>/', base_views.detail, name='detail'),
    path('answer/create/<int:question_id>/',
         answer_views.answer_create, name='answer_create'),
    path('answer/modify/<int:answer_id>/',
         answer_views.answer_modify, name='answer_modify'),
    path('answer/delete/<int:answer_id>/',
         answer_views.answer_delete, name='answer_delete'),
    path('question/create/', question_views.question_create, name='question_create'),
    path('question/modify/<int:question_id>/',
         question_views.question_modify, name='question_modify'),
    path('question/delete/<int:question_id>/',
         question_views.question_delete, name='question_delete'),
    path('question/vote/<int:question_id>/',
         question_views.question_vote, name='question_vote'),
    path('answer/vote/<int:answer_id>/',
         answer_views.answer_vote, name='answer_vote'),

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
