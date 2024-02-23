import logging

from django.contrib.sites.shortcuts import get_current_site
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet, Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tasks.forms import TasksHistoryDataForm
from tasks.models import Task, TasksHistory, TasksHistoryStatus, FileTypes, TasksHistoryData, CustomUser
from tasks.tokens import account_activation_token
from tasks.utility_file import FileUtilities

logger = logging.getLogger(__name__)
file_utilities = FileUtilities()


def get_default_task() -> Task:
    """
    Returns the default task
    """
    default_task_id = 1
    return Task.objects.get(id=default_task_id)


def assign_task(user: CustomUser, task: Task) -> None:
    """
    assign the task to the user
    """
    TasksHistory.objects.create(user=user, task=task, status=TasksHistoryStatus.ASSIGNED.value,
                                assigned_date=timezone.now())


def mark_task_as_submitted(task_history: TasksHistory) -> None:
    """
    The values of status and submitted date will be updated in the TaskHistory table to
    mark the assigned task as submitted.
    """
    task_history.submitted_date = timezone.now()
    task_history.status = TasksHistoryStatus.COMPLETED.value
    task_history.save()


def process_data(form: TasksHistoryDataForm, task_history: TasksHistory) -> None:
    text_data = form.cleaned_data['text_data']
    file_data = form.cleaned_data['file_data']
    if file_data is not None:
        original_file_name = file_data.name
        file_extension = file_utilities.get_file_extension(original_file_name)
    elif text_data != "" or text_data is not None:
        file_extension = ".txt"
        file_data = file_utilities.create_text_file(text_data, file_extension)
    else:
        raise ValueError("No data")

    file_type = file_utilities.get_file_type(file_extension)
    TasksHistoryData.objects.create(task_history=task_history, file_data=file_data, file_type=file_type,
                                    date_created=timezone.now())
    mark_task_as_submitted(task_history)


def get_new_task(user: CustomUser) -> Task:
    """
    Check task id which is not present in TaskHistory table for the user and get the lowest task id.
    Return the lowest task id as new task.
    """
    try:
        completed_tasks = TasksHistory.objects.filter(user=user).values_list('task', flat=True)
        new_task = Task.objects.exclude(id__in=completed_tasks).first()
    except Task.DoesNotExist as e:
        logger.error("No tasks are available to assign." + str(e))
        new_task = None

    return new_task


def get_user_experiences_data(object_list: QuerySet) -> list:
    """
    display all the completed tasks with experiences and make a private gallery to the user
    """
    user_experiences = []
    for task_history_data in object_list:
        task_id = task_history_data.task_history.task
        submitted_date = task_history_data.task_history.submitted_date
        file_type = task_history_data.file_type
        file = task_history_data.file_data
        if file_type == FileTypes.TEXT.value:
            data = file_utilities.read_text_file(file)
            user_experiences.append({"submitted_date": submitted_date, "task_id": task_id,
                                     "file_type": file_type, "file_data": data})
        else:
            user_experiences.append({"submitted_date": submitted_date, "task_id": task_id,
                                     "file_type": file_type, "file_data": file.url})
    if not len(user_experiences) == 0:
        logger.info("No tasks are completed for this user.")

    return user_experiences


def send_confirmation_mail(request: WSGIRequest, user: CustomUser) -> None:
    """
    send an activation link to the user's email id to confirm the account if user signed up
    """
    current_site = get_current_site(request)
    mail_subject = 'Welcome to MyxFate.com'
    messages = render_to_string('accounts/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject=mail_subject, message=messages)


def get_assigned_task_history(user: CustomUser) -> TasksHistory:
    """
    get task history of the assigned task for a user
    """
    try:
        task_history = TasksHistory.objects.get(Q(user=user), Q(status=TasksHistoryStatus.ASSIGNED.value))
    except Exception as e:
        logger.error("Problem while getting assigned task_history for this user: " + str(e))
        task_history = None

    return task_history


def get_task_history(user: CustomUser, task_id: int) -> TasksHistory:
    """
    Get task history for the specified user
    """
    try:
        task_history = TasksHistory.objects.get(Q(user=user), Q(task_id=task_id))
    except Exception as e:
        logger.error("Problem while getting task_history for this user: " + str(e))
        task_history = None

    return task_history
