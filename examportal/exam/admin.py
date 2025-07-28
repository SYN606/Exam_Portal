from django.contrib import admin
from .models import Exam, Question, Participant

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible', 'total_questions', 'duration')
    list_filter = ('visible',)
    search_fields = ('title',)
    list_editable = ('visible',)  # ✅ allows toggle directly in list view


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'correct_option')
    list_filter = ('exam',)
    search_fields = ('text',)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'exam', 'started_at')
    list_filter = ('exam',)
    search_fields = ('name', 'mobile')
