
from django.contrib import admin
from survey.models import *
from nested_admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline
from django.forms import TextInput, Textarea


class AnswerInline(NestedStackedInline):
    model = Answer
    extra = 0
    fields = (('product', 'show_users'), ('ru', 'uz'), 'next_question')
    formfield_overrides = {
		models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':30})},
	}

class QuestionInline(NestedStackedInline):
    model = Question
    inlines = [AnswerInline]
    extra = 0
    fields = (('ru', 'uz'), 'type', 'finish', 'num')

    formfield_overrides = {
		models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':30})},
	}


class PollAdmin(NestedModelAdmin):
    model = Poll
    inlines = [QuestionInline]
    list_display = ['name', 'status']

    formfield_overrides = {
		models.TextField: {'widget': Textarea(attrs={'rows':1, 'cols':40})},
	}

    # fields = ('name', 'status', )



class ResponseAdmin(NestedModelAdmin):
    model = Response
    list_display = ['user_id', 'response', 'question_id', 'date']








admin.site.register(Poll, PollAdmin)
# admin.site.register(Response, ResponseAdmin)

# Register your models here.
