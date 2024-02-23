import os
from unittest.mock import patch, mock_open, Mock

import pytest
from django.core import mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.files.uploadedfile import SimpleUploadedFile

from tasks.models import CustomUser
from tasks.models import TasksHistory, Task, TasksHistoryStatus, TasksHistoryData, FileTypes
from tasks.utility import get_default_task, mark_task_as_submitted, get_new_task, \
    assign_task, get_user_experiences_data, process_data, get_assigned_task_history, get_task_history


@pytest.mark.django_db
@pytest.mark.unit
def test_get_default_task():
    # assert that the first task is default task
    assert get_default_task().id == 1


@pytest.mark.django_db
@pytest.mark.unit
def test_assign_task():
    user = CustomUser.objects.get(pk=2)
    task = Task.objects.create(description="test your code", tips="abcd", created_date="2022-10-01")
    assign_task(user, task)
    # assert that the task assigned to the authenticated user in TaskHistory
    assert TasksHistory.objects.get(Q(user=user), Q(task=task), Q(status="ASSIGNED"))


@pytest.mark.unit
def test_mark_task_as_submitted():
    task_history = Mock()
    mark_task_as_submitted(task_history)
    # assert that the TaskHistory is updated when authenticated user completed the assigned task
    assert task_history.status == TasksHistoryStatus.COMPLETED.value
    task_history.save.assert_called()


@pytest.mark.integration
@pytest.mark.django_db
@patch('tasks.utility_file.FileUtilities.create_text_file')
def test_process_data(mock_create_text_file):
    task_history = TasksHistory.objects.get(pk=2)
    mock_form_class = Mock()
    mock_form_class.cleaned_data = {"text_data": "hello user", "file_data": None}
    mock_create_text_file.return_value = SimpleUploadedFile("test.txt", b"dummy data")
    process_data(mock_form_class, task_history)
    mock_create_text_file.assert_called_once()

    # assert that the submitted form data saved in TasksHistoryData
    assert TasksHistoryData.objects.get(Q(task_history=task_history), Q(file_type=FileTypes.TEXT.value))
    # assert that the assigned task to the user is completed
    assert task_history.status == TasksHistoryStatus.COMPLETED.value


@pytest.mark.django_db
@pytest.mark.unit
def test_get_new_task():
    user = CustomUser.objects.get(pk=2)
    new_task = Task.objects.create(description="test your code", tips="abcd", created_date="2022-10-01")

    # assert that the function returns the lowest Task(id) from the database if the task was not present in
    # The TaskHistory for given user
    assert get_new_task(user) == new_task


@pytest.mark.unit
@pytest.mark.django_db
@patch('os.makedirs')
@patch('__main__.__builtins__.open', new_callable=mock_open)
def test_get_user_experiences_data(mock_file, mock_dirs):
    task_history_data1 = TasksHistoryData.objects.get(pk=1)
    task_history_data2 = TasksHistoryData.objects.get(pk=2)
    object_list = [task_history_data1, task_history_data2]
    mock_file().read.return_value = b"demo text data"

    expected_list = [
        {"submitted_date": task_history_data1.task_history.submitted_date,
         "task_id": task_history_data1.task_history.task,
         "file_type": task_history_data1.file_type,
         "file_data": "demo text data",
         },
        {"submitted_date": task_history_data2.task_history.submitted_date,
         "task_id": task_history_data2.task_history.task,
         "file_type": task_history_data2.file_type,
         "file_data": task_history_data2.file_data.url,
         }
    ]
    # assert that the function get user's experiences list data with provided object list is matched
    # with expected list data
    assert get_user_experiences_data(object_list) == expected_list


@pytest.mark.integration
@pytest.mark.django_db
def test_send_confirmation_mail():
    user = CustomUser.objects.get(pk=3)
    subject = "Confirmation mail sent to you"
    expected_message = """
Hi taskuser,
    Please click on the link to confirm your account registration,
https://127.0.0.1:8000/account-activate/Mw/bf5cds-8cf51fcb71eafb10a98423506e2810cf/

"""

    message = render_to_string('accounts/acc_active_email.html', {
        'user': user,
        'domain': "127.0.0.1:8000",
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token': 'bf5cds-8cf51fcb71eafb10a98423506e2810cf',
    })
    user.email_user(subject, message)
    """
    Django’s test runner automatically redirects all Django-sent email to a dummy outbox. The test runner 
    accomplishes this by transparently replacing the normal email backend with a testing backend. During 
    test running, each outgoing email is saved in django.core.mail.outbox.
    """
    # assert that mail Inbox is not empty
    assert len(mail.outbox) == 1
    # assert message sent to the given user is matched with expected message
    assert mail.outbox[0].body + "" == expected_message
    # assert that the mail was received by the given user at email ID
    assert mail.outbox[0].to == [user.email]


@pytest.mark.unit
@pytest.mark.django_db
def test_get_assigned_task_history():
    user = CustomUser.objects.get(id=2)
    # assert that the function return task_history if any task is assigned to the user
    assert get_assigned_task_history(user)


@pytest.mark.unit
@pytest.mark.django_db
def test_get_task_history():
    user = CustomUser.objects.get(id=2)
    task_id = 2
    # assert that the function return task_history if the status of given task id is assigned or completed by the user
    assert get_task_history(user, task_id)

    # check task_history is none if the status of given new task id is not assigned or completed by the user
    new_task_id = 5
    assert get_task_history(user, new_task_id) is None
