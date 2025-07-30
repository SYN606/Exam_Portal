from django.contrib import admin
from django.http import HttpResponse
import csv
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
    actions = ['export_as_csv']  # ✅ Added export action

    def exam_date(self, obj):
        return obj.started_at.date()
    exam_date.short_description = 'Date'

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="participants.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Mobile', 'Exam', 'Score', 'Date'])

        for participant in queryset:
            writer.writerow([
                participant.name,
                participant.mobile,
                participant.exam.title,
                getattr(participant, 'score', 0),
                participant.started_at.date()
            ])

        return response

    export_as_csv.short_description = "Export Selected Participants to CSV"
