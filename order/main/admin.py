from django.contrib import admin
from main.models import Question
# Register your models here.


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']


admin.site.register(Question, QuestionAdmin)
