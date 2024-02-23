import os

import pytest
from django.core.management import call_command

from humdrum.settings.settings_local import BASE_DIR
from tasks.utility_file import FileUtilities

file_path = os.path.join(BASE_DIR, 'relative_path')


@pytest.fixture(scope='function')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        test_db_file_path = os.path.join(BASE_DIR, 'tasks/tests/test_data/test_db.json')
        call_command('loaddata', test_db_file_path)


@pytest.fixture(scope='function')
def file_utilities():
    return FileUtilities()
