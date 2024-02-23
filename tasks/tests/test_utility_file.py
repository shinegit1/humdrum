from unittest.mock import patch

import pytest as pytest


@pytest.mark.unit
def test_get_all_valid_extensions(file_utilities):
    expected_extensions = ['.png', '.jpg', '.jpeg', '.mp3', '.ogg', '.wav', '.mp4', '.webm', '.txt']
    # assert that the function returns all the extensions that we accept.
    assert file_utilities.get_all_valid_file_extensions() == expected_extensions


@pytest.mark.unit
def test_get_file_type(file_utilities):
    expected_file_type = "IMAGE"
    # assert that the function returns the correct file type for a particular extension.
    assert file_utilities.get_file_type(".jpg") == expected_file_type


@pytest.mark.unit
def test_get_valid_extensions_list(file_utilities):
    expected_extension_list = ['.png', '.jpg', '.jpeg']
    # assert that the function returns the correction extension list for a particular file type.
    assert file_utilities.get_valid_file_extensions_list("IMAGE") == expected_extension_list


@pytest.mark.unit
def test_get_file_extension(file_utilities):
    expected_extension = ".txt"
    # assert that the function returns the extension of the file.
    assert file_utilities.get_file_extension("test.txt") == expected_extension


@pytest.mark.unit
@patch('tasks.utility_file.uuid4')
def test_get_unique_file_name(mock_uuid4, file_utilities):
    extension = '.txt'
    mock_uuid4().hex = "abcd1234"
    expected_file_name = "abcd1234.txt"
    # assert that the function returns the unique file name with the provided extension
    assert file_utilities.get_unique_file_name(extension) == expected_file_name
