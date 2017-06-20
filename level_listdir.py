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

    def __init__(self, path, level):
        self.get_path(path, level)

    def get_path(self, parent_dir, level):
        result_dirs = [join(parent_dir, d) for d in listdir(parent_dir) if isdir(join(parent_dir, d))]
        if result_dirs.__len__().__eq__(0):
            return result_dirs
        else:
            tmp = []
            for d in result_dirs:
                tmp.extend(self.get_path(d, level - 1))
            result_dirs.extend(d)
            return result_dirs
