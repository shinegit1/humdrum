import enum

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from tasks.utility_file import FileTypes, FileUtilities


class CustomUser(AbstractUser):
    username_validator = ASCIIUsernameValidator()
    username = models.CharField(_("username"),
                                max_length=150,
                                unique=True,
                                help_text=_("Required. letters, digits and @/./+/-/_ only."),
                                validators=[username_validator],
                                error_messages={
                                    "unique": _("A user with that username already exists."),
                                }, )
    email = models.EmailField(_("email address"),
                              unique=True,
                              error_messages={
                                  "unique": _("A user with that email address already exists."),
                              }, )

    def clean(self):
        self.username = self.username.lower()
        self.email = self.__class__.objects.normalize_email(self.email).lower()
        super().clean()


class Task(models.Model):
    description = models.CharField(max_length=600)
    tips = models.TextField(max_length=2000)
    created_date = models.DateField()

    def get_absolute_url(self):
        return reverse_lazy('tasks:Taskboard', kwargs={"task_id": self.id})


class TasksHistoryStatus(enum.Enum):
    ASSIGNED = 'ASSIGNED'
    COMPLETED = 'COMPLETED'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class TasksHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_index=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    submitted_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TasksHistoryStatus.choices())
    assigned_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # if we are trying to assign the task which is already assigned or completed by the user
        if self.status == TasksHistoryStatus.ASSIGNED.value and len(
                TasksHistory.objects.filter(user=self.user, task=self.task)) >= 1:
            raise ValueError("Task for this user is already assigned or completed.")
        super(TasksHistory, self).save(*args, **kwargs)


class TasksHistoryData(models.Model):
    def customer_data_path(self, filename):
        # file will be uploaded to MEDIA_ROOT/<username>/<file_type>/<filename>
        return f'{self.task_history.user}/{self.file_type}/{filename}'

    task_history: TasksHistory = models.ForeignKey(TasksHistory, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=10, choices=FileTypes.choices())
    file_data = models.FileField(upload_to=customer_data_path,
                                 validators=[FileExtensionValidator(FileUtilities().get_all_valid_file_extensions())],
                                 default="None")
    date_created = models.DateTimeField(null=True, blank=True)
