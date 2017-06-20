#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""
from os import listdir
from os.path import join, isdir


class LevelListDir:
    """
    I do not know yet.
    """

    RESULT_LIST = []
    PARENT_DIR = []
    LEVEL = 0

    def __int__(self, parent_dir, level):
        self.PARENT_DIR = parent_dir
        self.LEVEL = level

    @staticmethod
    def get_path_content(parent_dir):
        result_dirs = []
        try:
            result_dirs = [join(parent_dir, d) for d in listdir(parent_dir) if isdir(join(parent_dir, d))]
            print("i am here")
        except PermissionError as e:
            print(str(e))
        except FileNotFoundError as e:
            print(str(e))
        finally:
            return result_dirs

    def persist_path(self, path_list):
        self.RESULT_LIST.extend(path_list)
