from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    class SecurityQuestion(models.TextChoices):
        PET = "PET", "What was the name of your first pet?"
        SCHOOL = "SCHOOL", "What primary school did you attend?"
        CITY = "CITY", "In what city were you born?"
        MOTHER = "MOTHER", "What is your mother's maiden name?"

    role = models.CharField(max_length=10,
                            choices=Role.choices,
                            default=Role.STUDENT)

    security_question = models.CharField(max_length=20,
                                         choices=SecurityQuestion.choices,
                                         blank=True,
                                         null=True)
    security_answer = models.CharField(max_length=255,
                                       blank=True,
                                       null=True,
                                       help_text="Stored as a secure hash.")

    # Fix reverse accessor clashes with default auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set_permissions',
        related_query_name='user',
    )

    def set_security_answer(self, raw_answer: str):
        """Hashes the security answer in lowercase to ensure case-insensitive matching."""
        if raw_answer:
            self.security_answer = make_password(raw_answer.strip().lower())

    def check_security_answer(self, raw_answer: str) -> bool:
        """Verifies the input against the stored answer hash."""
        if not self.security_answer or not raw_answer:
            return False
        return check_password(raw_answer.strip().lower(), self.security_answer)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
            self.is_staff = True
        elif self.role in [self.Role.ADMIN, self.Role.TEACHER]:
            self.is_staff = True
        else:
            self.is_staff = False

        super().save(*args, **kwargs)
