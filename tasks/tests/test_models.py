import pytest

from tasks.models import Task, TasksHistory, CustomUser


@pytest.mark.django_db
@pytest.mark.unit
def test_task_history():
    user_id = CustomUser.objects.get(pk=2)
    task_id = Task.objects.get(pk=2)

    # check the exception occur when we save assigned task as completed of authenticated user in TasksHistory
    with pytest.raises(ValueError):
        TasksHistory.objects.create(user=user_id, task=task_id, status="ASSIGNED",
                                    assigned_date="2022-10-31T17:59:56.970Z")
