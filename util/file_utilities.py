import configparser
import os
import shutil
import sys
import uuid
from pathlib import Path


class FileUtilities:

    @staticmethod
    def get_platform():
        platforms={
            'linux1': 'Linux',
            'linux2': 'Linux',
            'darwin': 'OS X',
            'win32': 'Windows'
        }
        if sys.platform not in platforms:
            return sys.platform
        return platforms[sys.platform]

    @staticmethod
    def get_data_path():
        config=configparser.ConfigParser()
        config.read('./config.ini')
        data_folder = config.get('APP',"DATA_FOLDER",fallback=os.path.join(str(Path.home()),"data"))
        if not os.path.exists(data_folder):
            os.makedirs(data_folder, exist_ok=True)
        return data_folder

    @staticmethod
    def clear_folder(folder_path):
        for file_object in os.listdir(folder_path):
            file_object_path=os.path.join(folder_path,file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

    @staticmethod
    def create_new_folder(path):
        assert os.path.isdir(path), "invalid parameters"
        try:
            while True:
                new_folder = os.path.join(path, str(uuid.uuid4()))
                if not os.path.exists(new_folder):
                    os.mkdir(new_folder)
                    break
        except Exception as ex:
            raise ex
        return new_folder
