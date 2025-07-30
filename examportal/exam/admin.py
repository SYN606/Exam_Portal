from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import io

from .models import Exam, Question, Participant

# ✅ Exam Admin
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible', 'total_questions', 'duration')
    list_filter = ('visible',)
    search_fields = ('title',)
    list_editable = ('visible',)


# ✅ Participant Admin with CSV export
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'exam', 'score', 'exam_date')
    list_filter = ('exam',)
    search_fields = ('name', 'mobile')
    actions = ['export_as_csv']

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


# ✅ Question Admin with CSV import
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'correct_option')
    list_filter = ('exam',)
    search_fields = ('text',)
    change_list_template = "admin/question_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv)
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST" and request.FILES.get("csv_file") and request.POST.get("exam_id"):
            csv_file = request.FILES["csv_file"]
            exam_id = request.POST.get("exam_id")

            decoded_file = csv_file.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            count = 0
            for row in reader:
                Question.objects.create(
                    exam_id=exam_id,
                    text=row['text'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_option=row['correct_option'].upper().strip()
                )
                count += 1

            messages.success(request, f"✅ Imported {count} questions successfully.")
            return redirect("..")

        exams = Exam.objects.all()
        return render(request, "admin/import_questions.html", {'exams': exams})
