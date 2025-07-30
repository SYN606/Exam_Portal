from django.contrib import admin
from .models import Exam, Question, Participant

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible', 'total_questions', 'duration')
    list_filter = ('visible',)
    search_fields = ('title',)
    list_editable = ('visible',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'correct_option')
    list_filter = ('exam',)
    search_fields = ('text',)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'exam', 'score', 'exam_date')
    list_filter = ('exam',)
    search_fields = ('name', 'mobile')

    def exam_date(self, obj):
        return obj.started_at.date()
    exam_date.short_description = 'Date'
