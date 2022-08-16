from django.urls import path
from main.views import base_views, answer_views, question_views

app_name = 'main'

urlpatterns = [
    path('', base_views.index, name='index'),
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
]
