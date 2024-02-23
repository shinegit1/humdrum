from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.forms import CustomUserChangeForm, UserSignupForm
from tasks.models import CustomUser
from tasks.models import Task


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = UserSignupForm
    model = CustomUser
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    class Meta:
        model = Task
        fields = ['__all__']

    list_display = ['id', 'description', 'tips', 'created_date']
