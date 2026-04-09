from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render, redirect
import csv
import io

from .models import Exam, Question, Participant, Option


# =======================
# EXAM ADMIN
# =======================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "total_questions", "duration")
    list_filter = ("is_active",)
    search_fields = ("title",)
    list_editable = ("is_active",)


# =======================
# PARTICIPANT ADMIN (FIXED)
# =======================
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "exam", "score", "exam_date", "is_submitted")
    list_filter = ("exam", "is_submitted")
    search_fields = ("user__username",)
    actions = ["export_as_csv"]

    def exam_date(self, obj):
        return obj.started_at.date()

    exam_date.short_description = "Date"

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="participants.csv"'

        writer = csv.writer(response)
        writer.writerow(["Username", "Exam", "Score", "Date", "Submitted"])

        for participant in queryset:
            writer.writerow(
                [
                    participant.user.username,
                    participant.exam.title,
                    participant.score,
                    participant.started_at.date(),
                    participant.is_submitted,
                ]
            )

        return response

    export_as_csv.short_description = "Export selected participants"


# =======================
# INLINE OPTION ADMIN
# =======================
class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


# =======================
# QUESTION ADMIN
# =======================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "exam", "order")
    list_filter = ("exam",)
    search_fields = ("text",)
    inlines = [OptionInline]
    change_list_template = "admin/question_changelist.html"

    def short_text(self, obj):
        return obj.text[:50]

    short_text.short_description = "Question"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv, name="import_questions_csv"),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            exam_id = request.POST.get("exam_id")

            if not csv_file or not exam_id:
                messages.error(request, "Missing file or exam selection")
                return redirect(request.path)

            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Only CSV files are allowed")
                return redirect(request.path)

            try:
                decoded = csv_file.read().decode("utf-8")
                io_string = io.StringIO(decoded)
                reader = csv.DictReader(io_string)

                count = 0

                for row in reader:
                    question = Question.objects.create(
                        exam_id=exam_id, text=row.get("question", "").strip()
                    )

                    options = [
                        ("A", row.get("option_a")),
                        ("B", row.get("option_b")),
                        ("C", row.get("option_c")),
                        ("D", row.get("option_d")),
                    ]

                    correct = row.get("correct_option", "").strip().upper()

                    for key, text in options:
                        if text:
                            Option.objects.create(
                                question=question,
                                text=text.strip(),
                                is_correct=(key == correct),
                            )

                    count += 1

                messages.success(request, f"Successfully imported {count} questions")
                return redirect("..")

            except Exception as e:
                messages.error(request, f"Import failed: {str(e)}")
                return redirect(request.path)

        exams = Exam.objects.all()
        return render(request, "admin/import_questions.html", {"exams": exams})