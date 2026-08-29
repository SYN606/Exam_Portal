from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser',
                    'is_active', 'date_joined')

    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined', )

    readonly_fields = ('security_answer', )

    fieldsets = list(BaseUserAdmin.fieldsets or []) + [
        (_('Custom Profile Info'), {
            'fields': ('role', )
        }),
        (_('Security Recovery'), {
            'fields': ('security_question', 'security_answer'),
            'description':
            _('Note: The security answer is stored as a secure hash. '
              'Use custom user methods to update it safely.')
        })
    ]

    add_fieldsets = list(BaseUserAdmin.add_fieldsets
                         or []) + [(_('Custom Profile Info'), {
                             'classes': ('wide', ),
                             'fields': ('role', 'security_question'),
                         })]
