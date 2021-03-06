from django.contrib import admin
from .models import Question,Choice
class ChoiceInline(admin.TabularInline):
    model=Choice
    extra = 1
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_state', 'was_published_recently')
    list_filter=['pub_state','question_text',]
    search_fields=['question_text','pub_state']
    # fieldsets = [
    #     (None,{'fields': ['question_text']}),
    #     ('Date information', {'fields': ['pub_state'],'classes':['collapse']}),
        
    # ]
    # inlines=[ChoiceInline]
    # fields=['pub_state','question_text']
admin.site.register(Question,QuestionAdmin)
# admin.site.register(Choice)
# Register your models here.
