import os
from http.client import HTTPException
from unittest.mock import patch, mock_open

import pytest
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pytest_django.asserts import assertRedirects

from tasks.models import TasksHistory, TasksHistoryData, Task, TasksHistoryStatus, CustomUser
from tasks.tokens import account_activation_token
from tasks.utility import get_assigned_task_history
from tasks.views import HomePageView


@pytest.mark.django_db
@pytest.mark.integration
def test_home_page_view(rf, client):
    home_page_url = "/"
    request1 = rf.get(home_page_url)
    view = HomePageView()
    view.setup(request1)

    context = view.get_context_data()
    # assert that home page shows the first task to the user
    assert context['task'].id == 1

    client.login(username="user1", password="Password@123")
    user = CustomUser.objects.get(username="user1")

    task_history = get_assigned_task_history(user=user)
    expected_url_1 = "/challenge/{}/".format(task_history.task.id)
    response1 = client.get(home_page_url)
    # assert that the HomePageView redirect to the expected url if a task is assigned to the authenticated user
    assertRedirects(response1, expected_url=expected_url_1, status_code=302)

    # update task history status from assigned to completed
    task_history.status = TasksHistoryStatus.COMPLETED.value
    task_history.save()
    # now all challenges of Task table is completed by a user in Task History
    expected_url_2 = "/upcoming-challenge/"
    response2 = client.get(home_page_url)
    # assert that HomePageView redirected to the expected url if no more task is existed in database to assign
    assertRedirects(response2, expected_url=expected_url_2, status_code=302)

    # create a new task
    task = Task.objects.create(description="test your code", tips="abcd", created_date="2022-10-01")
    expected_url_3 = "/challenge/{}/".format(task.id)
    response3 = client.get(home_page_url)
    # assert that the HomePageView redirected to the expected url if created task assigned to the user
    assertRedirects(response3, expected_url=expected_url_3, status_code=302)


@pytest.mark.django_db
@pytest.mark.unit
def test_upcoming_task_view(client):
    url = "/upcoming-challenge/"
    client.login(username="user1", password="Password@123")
    response = client.get(url)

    # assert that the response's status code is matched with 200 (success)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.integration
def test_urls_with_login_required(client):
    url_list = ["/challenge/1/", "/submit-data/1/", "/logout/"]

    # default user is anonymous
    # assert that the anonymous user is redirected to login page

    for url in url_list:
        response = client.get(url)
        expected_url = '/login/' + "?next=" + url
        assertRedirects(response, expected_url=expected_url, status_code=302, fetch_redirect_response=False)


@pytest.mark.django_db
@pytest.mark.integration
def test_task_view(client):
    # assert that the authenticated user is presented with taskview
    client.login(username="user1", password="Password@123")
    # get user from test_data/test_db.json
    user = CustomUser.objects.get(id=2)

    url_1 = "/challenge/{}/".format(2)
    expected_task_history1 = TasksHistory.objects.get(Q(user=user), Q(task_id=2),
                                                      Q(status=TasksHistoryStatus.ASSIGNED.value))
    response1 = client.get(url_1)
    # assert that expected task history matched with the value of response's context key 'task_history'
    # if the status of coming task id in url is assigned to a user
    assert response1.context['task_history'] == expected_task_history1
    assert response1.context['task'].id == 2

    url_2 = "/challenge/{}/".format(1)
    expected_task_history2 = TasksHistory.objects.get(Q(user=user), Q(task_id=1),
                                                      Q(status=TasksHistoryStatus.COMPLETED.value))
    response2 = client.get(url_2)
    # assert that expected task history matched with the value of response's context key 'task_history'
    # if the status of coming task id in url is completed for a user
    assert response2.context['task_history'] == expected_task_history2
    assert response2.context['task'].id == 1

    # create a new task
    task = Task.objects.create(description="test your code", tips="abcd", created_date="2022-10-01")

    # assert that the created task exists in the database but its status is not assigned or completed
    # for a user in task history
    with pytest.raises(TasksHistory.DoesNotExist):
        TasksHistory.objects.get(Q(user=user, task_id=task.id))


@pytest.mark.django_db
@pytest.mark.integration
@patch('tasks.utility.get_new_task')
@patch('__main__.__builtins__.open', new_callable=mock_open)
def test_submit_data_view(mock_task, mock_file_path, client):
    task_history = TasksHistory.objects.get(pk=2)
    submit_data_url = "/submit-data/{}/".format(task_history.id)

    # get client user from test_data/test_db.json
    # assert that the authenticated user is presented with dashboard view
    user = CustomUser.objects.get(pk=2)
    client.login(username=user.username, password="Password@123")
    response1 = client.get(submit_data_url)
    assert response1.status_code == 200

    # post new form-data and check if page is redirected
    form_data = {"text_data": "hello user"}
    mock_file_path.return_value = "media_files" + os.sep + user.username + os.sep + "TEXT"
    mock_task.return_value = Task.objects.create(description="new task", tips="test it.", created_date="2022-10-01")
    response3 = client.post(submit_data_url, form_data)
    assert response3.status_code == 302

    # assert that entries are created in database
    assert TasksHistory.objects.get(Q(user=user), Q(task=task_history.task),
                                    Q(status=TasksHistoryStatus.COMPLETED.value))
    assert TasksHistoryData.objects.get(task_history=task_history)


@pytest.mark.django_db
@pytest.mark.integration
@patch('__main__.__builtins__.open', new_callable=mock_open)
def test_my_experience_view(mock_file, client):
    my_experience_url = "/my-experiences/1/"
    client.login(username="user1", password="Password@123")

    # get all tasksHistoryData submitted by the authenticated user
    task_history_data = TasksHistoryData.objects.get(pk=1)
    task_history_data1 = TasksHistoryData.objects.get(pk=2)

    # return read text data from text file
    mock_file().read.return_value = b"demo text"

    expected_experiences = [
        {"submitted_date": task_history_data1.task_history.submitted_date,
         "task_id": task_history_data1.task_history.task,
         "file_type": task_history_data1.file_type,
         "file_data": task_history_data1.file_data.url,
         },
        {"submitted_date": task_history_data.task_history.submitted_date,
         "task_id": task_history_data.task_history.task,
         "file_type": task_history_data.file_type,
         "file_data": "demo text",
         },
    ]
    # assert that the user experiences data redirect to the expected url
    response = client.get(my_experience_url, {"user_experiences": expected_experiences})
    assert response.status_code == 200

    # assert that expected experiences matched with the value of response's context key 'user_experiences'
    assert response.context['user_experiences'] == expected_experiences


@pytest.mark.django_db
@pytest.mark.integration
@patch('tasks.views.send_confirmation_mail')
def test_sign_up_view(mock_send_confirmation_mail, client):
    sign_up_url = "/signup/"
    response1 = client.get(sign_up_url)
    assert response1.status_code == 200

    # post the signup data to create a new user and assert that the page is redirected
    data = {"username": "taskuser1", "email": "taskuser1@gmail.com", "password1": "Password@123",
            "password2": "Password@123"}
    response2 = client.post(sign_up_url, data)
    assert response2.status_code == 302

    mock_send_confirmation_mail.side_effect = HTTPException()
    data1 = {"username": "taskuser2", "email": "taskuser2@gmail.com", "password1": "Password@123",
             "password2": "Password@123"}

    # assert that an exception raised and newly created account is deleted if send confirmation_email function fails
    with pytest.raises(Exception) as e:
        client.post(sign_up_url, data1)
        assert CustomUser.objects.filter(username='taskuser2').exists() is False


@pytest.mark.django_db
@pytest.mark.integration
def test_activate_account(client):
    # get the inactive user from the database
    user1 = CustomUser.objects.get(pk=3)
    uid = urlsafe_base64_encode(force_bytes(user1.id))
    # create a valid token to the user and pass it as an argument in the url link
    token = account_activation_token.make_token(user1)
    valid_activate_url = "/account-activate/{}/{}/".format(uid, token)
    # assert page is redirect if the link is valid
    response1 = client.get(valid_activate_url)
    assert response1.status_code == 302
    assert user1.is_authenticated

    # Create a new user and make it inactive
    user2 = CustomUser.objects.create_user(username='myuser', email='myuser@gmail.com', password='Password@123')
    user2.is_active = False
    user2.save()
    uid2 = urlsafe_base64_encode(force_bytes(user2.id))
    # create an invalid token to the user and pass it as an argument in the url link
    invalid_token = 'abcd'
    invalid_activate_url = "/account-activate/{}/{}/".format(uid2, invalid_token)
    # assert that an exception is raised if link is invalid
    with pytest.raises(Exception):
        client.get(invalid_activate_url)
        assert user2.is_authenticated is False


@pytest.mark.django_db
def test_log_out_view(client):
    redirect_url = reverse_lazy('tasks:HomePage')
    user = CustomUser.objects.get(username="user1")
    # client user is authenticated
    client.force_login(user)

    # assert that the client user is unauthenticated if the page is redirected
    response1 = client.get("/logout/")
    assertRedirects(response1, status_code=301, expected_url=redirect_url)


@pytest.mark.integration
def test_privacy_policy_view(client):
    policy_url = "/privacy-policy/"

    response = client.get(policy_url)
    # assert that the response's status code is matched with 200 (success)
    assert response.status_code == 200


@pytest.mark.integration
def test_terms_of_use_view(client):
    terms_of_use_url = "/terms-of-use/"

    response = client.get(terms_of_use_url)
    # assert that the response's status code is matched with 200 (success)
    assert response.status_code == 200


@pytest.mark.integration
def test_about_us_page_view(client):
    about_us_url = "/about-us/"

    response = client.get(about_us_url)
    # assert that the response's status code is matched with 200 (success)
    assert response.status_code == 200
