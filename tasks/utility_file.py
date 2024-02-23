import enum
import io
import logging
import os
from uuid import uuid4

from django.core.files import File

logger = logging.getLogger(__name__)


class FileTypes(enum.Enum):
    AUDIO = "AUDIO"
    VIDEO = 'VIDEO'
    IMAGE = 'IMAGE'
    TEXT = 'TEXT'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class FileUtilities:
    def __init__(self):
        self._valid_file_extension_mapping = {
            FileTypes.IMAGE.value: ['.png', '.jpg', '.jpeg'],
            FileTypes.AUDIO.value: ['.mp3', '.ogg', '.wav'],
            FileTypes.VIDEO.value: ['.mp4', '.webm'],
            FileTypes.TEXT.value: ['.txt']
        }

    def get_file_type(self, file_extension: str) -> str:
        """
        Here, we match valid file type of uploaded file extension in FILE_EXTENSION_LIST with value of FileTypes
        and return file type
        """
        for file_type, file_extensions in self._valid_file_extension_mapping.items():
            if file_extension in file_extensions:
                return file_type
        raise ValueError('Invalid file extension passed.')

    def get_valid_file_extensions_list(self, file_type: str) -> list:
        """
        Returns the valid file extensions for a particular file type.
        :param file_type:
        :return:
        """
        if file_type in self._valid_file_extension_mapping:
            return self._valid_file_extension_mapping[file_type]
        else:
            raise ValueError("Invalid file type passed.")

    def get_all_valid_file_extensions(self) -> list:
        """
        Returns all the valid extensions that we accept irrespective of file type.
        :return:
        """
        all_valid_file_extensions = []
        for file_type, file_extensions in self._valid_file_extension_mapping.items():
            all_valid_file_extensions.extend(file_extensions)
        return all_valid_file_extensions

    @staticmethod
    def get_unique_file_name(extension: str) -> str:
        """
        Returns a new file name by generating random 8 characters to make the file name unique
        """
        return uuid4().hex[0:8] + extension

    @staticmethod
    def get_file_extension(file_name: str) -> str:
        """
        extract file extension from uploaded file
        """
        file_extension = os.path.splitext(file_name)[1]
        return file_extension

    def create_text_file(self, text_data: str, file_extension: str) -> File:
        """
        Creates django text file with unique name from text data.
        :param file_extension:
        :param text_data:
        :return:
        """
        return File(io.StringIO(text_data), name=self.get_unique_file_name(file_extension))

    @staticmethod
    def read_text_file(file: File) -> str:
        """
        Opens a text file in binary mode and return the string.
        :param file:
        :return:
        """
        # this syntax is for django implementation of File object.
        with file.open('rb') as f:
            data = f.read().decode()
        return data
