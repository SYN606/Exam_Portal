import csv
import io
from typing import Any

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path

from .models import Exam, Option, Participant, Question


# INLINE OPTION ADMIN
class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


# EXAM ADMIN
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "is_active", "total_questions",
                    "duration")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    list_editable = ("is_active", )
    readonly_fields = ("created_by", )

    def save_model(self, request: HttpRequest, obj: Exam, form: Any,
                   change: bool) -> None:
        if not obj.pk and not request.user.is_superuser:
            obj.created_by = request.user  # type: ignore
        super().save_model(request, obj, form, change)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Exam]:
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, "role",
                                                "") == "ADMIN":
            return qs
        return qs.filter(created_by=request.user)


# QUESTION ADMIN
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "exam", "order")
    list_filter = ("exam", )
    search_fields = ("text", )
    inlines = [OptionInline]
    change_list_template = "admin/question_changelist.html"

    @admin.display(description="Question")
    def short_text(self, obj: Question) -> str:
        return obj.text[:50]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, "role",
                                                "") == "ADMIN":
            return qs
        return qs.filter(exam__created_by=request.user)

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest,
                                 **kwargs: Any) -> Any:
        if db_field.name == "exam" and not (request.user.is_superuser
                                            or getattr(request.user, "role",
                                                       "") == "ADMIN"):
            kwargs["queryset"] = Exam.objects.filter(created_by=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self) -> list[Any]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-csv/",
                self.admin_site.admin_view(self.import_csv),
                name="import_questions_csv",
            ),
        ]
        return custom_urls + urls

    def import_csv(
            self, request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            exam_id = request.POST.get("exam_id")

            if not csv_file or not exam_id:
                messages.error(
                    request,
                    "Please provide both an exam selection and a CSV file.")
                return redirect(request.path)

            if not csv_file.name.endswith(".csv"):
                messages.error(
                    request, "Invalid file format. Please upload a .csv file.")
                return redirect(request.path)

            exam = Exam.objects.filter(id=exam_id).first()
            is_admin = (request.user.is_superuser
                        or getattr(request.user, "role", "") == "ADMIN")
            if not exam or (not is_admin and exam.created_by != request.user):
                messages.error(request,
                               "Permission denied or exam does not exist.")
                return redirect(request.path)

            try:
                decoded_file = csv_file.read().decode("utf-8-sig")
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)

                required_fields = {
                    "question",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_option",
                }
                if not reader.fieldnames or not required_fields.issubset(
                        set(reader.fieldnames)):
                    messages.error(
                        request,
                        "Invalid CSV headers. Required: question, option_a, option_b, option_c, option_d, correct_option",
                    )
                    return redirect(request.path)

                imported_count = 0
                errors: list[str] = []

                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        question_text = (row.get("question") or "").strip()
                        correct_option = ((row.get("correct_option")
                                           or "").strip().upper())

                        if not question_text:
                            errors.append(
                                f"Row {row_num}: Missing question text.")
                            continue

                        if correct_option not in ["A", "B", "C", "D"]:
                            errors.append(
                                f"Row {row_num}: Invalid 'correct_option' (must be A, B, C, or D)."
                            )
                            continue

                        options_map = [
                            ("A", (row.get("option_a") or "").strip()),
                            ("B", (row.get("option_b") or "").strip()),
                            ("C", (row.get("option_c") or "").strip()),
                            ("D", (row.get("option_d") or "").strip()),
                        ]

                        valid_options = [(key, txt) for key, txt in options_map
                                         if txt]
                        if len(valid_options) < 2:
                            errors.append(
                                f"Row {row_num}: Question must have at least 2 non-empty options."
                            )
                            continue

                        question = Question.objects.create(exam=exam,
                                                           text=question_text)

                        options_to_create = [
                            Option(
                                question=question,
                                text=text,
                                is_correct=(key == correct_option),
                            ) for key, text in valid_options
                        ]
                        Option.objects.bulk_create(options_to_create)
                        imported_count += 1

                    if errors and imported_count == 0:
                        transaction.set_rollback(True)
                        for err in errors[:5]:
                            messages.error(request, err)
                        return redirect(request.path)

                if errors:
                    messages.warning(
                        request,
                        f"Imported {imported_count} questions with warnings. Skipped {len(errors)} invalid rows.",
                    )
                else:
                    messages.success(
                        request,
                        f"Successfully imported {imported_count} questions into '{exam.title}'.",
                    )

                return redirect("admin:exam_question_changelist")

            except UnicodeDecodeError:
                messages.error(
                    request,
                    "Encoding error: Please ensure the CSV file is UTF-8 encoded.",
                )
                return redirect(request.path)
            except Exception as e:
                messages.error(
                    request,
                    f"An unexpected error occurred during import: {str(e)}")
                return redirect(request.path)

        if request.user.is_superuser or getattr(request.user, "role",
                                                "") == "ADMIN":
            exams = Exam.objects.all()
        else:
            exams = Exam.objects.filter(created_by=request.user)

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Import Questions from CSV",
            "exams": exams,
        }
        return render(request, "admin/import_questions.html", context)


# PARTICIPANT ADMIN
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "exam", "score", "exam_date", "is_submitted")
    list_filter = ("exam", "is_submitted")
    search_fields = ("user__username", "user__email")
    actions = ["export_as_csv"]

    @admin.display(description="Date")
    def exam_date(self, obj: Participant) -> Any:
        return obj.started_at.date() if obj.started_at else None

    def get_queryset(self, request: HttpRequest) -> QuerySet[Participant]:
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, "role",
                                                "") == "ADMIN":
            return qs
        return qs.filter(exam__created_by=request.user)

    @admin.action(description="Export selected participants")
    def export_as_csv(self, request: HttpRequest,
                      queryset: QuerySet[Participant]) -> HttpResponse:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="participants.csv"')

        writer = csv.writer(response)
        writer.writerow(["Username", "Exam", "Score", "Date", "Submitted"])

        for participant in queryset:
            date_val = (participant.started_at.date()
                        if participant.started_at else "")
            writer.writerow([
                participant.user.username if participant.user else "",
                participant.exam.title if participant.exam else "",
                participant.score,
                date_val,
                participant.is_submitted,
            ])

        return response
