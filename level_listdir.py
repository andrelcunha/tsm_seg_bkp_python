#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""

from os import listdir, chdir
from os.path import join, isdir
from random import choice
from string import ascii_uppercase, digits
from tempfile import TemporaryDirectory


class LevelListDir:
    """
    I do not know yet.
    """

    def __init__(self, parent_dir, level=0):
        self.BASE_DIR = parent_dir
        self.LEVEL = level
        self._FILELEVEL_LIST = []
        self.TMP_DIR = TemporaryDirectory(prefix="bkp_seg_python_")
        chdir(self.TMP_DIR.name)
        self._main()

    @staticmethod
    def _get_path_content(parent_dir):
        """
        Get the content (directories) of a single path.
        :param parent_dir:
        :return:
        """
        path_list = []
        try:
            for d in listdir(parent_dir):
                dir_name = join(parent_dir, d)
                if isdir(dir_name):
                    path_list.append(dir_name)
        except PermissionError as e:
            print(str(e))
        except FileNotFoundError as e:
            print(str(e))
        finally:
            return path_list

    def _get_level_path_list(self, parent_dir_list):
        """
        Get a list of directories in a level directory and lists the sub dirs on each dir.
        In the end, returns a list of all the next sublevel
        :param parent_dir_list:
        :return:
        """
        path_list = []
        for parent_dir in parent_dir_list:
            path_list.extend(self._get_path_content(parent_dir))
        return path_list

    @staticmethod
    def _persist_path_list(path_list, level):
        file_level = ''.join(choice(ascii_uppercase + digits) for _ in range(6))
        file_level += 'TMP_LEVEL_' + str(level)
        with open(file_level, mode="w") as fl:
            for line in path_list:
                fl.write(line)
        return file_level

    def file_level_2_path_list(self, level):
        print(str(level))
        path_list = []
        file_level = self._FILELEVEL_LIST[level]
        with open(file_level, mode="r") as fll:
            for line in fll:
                path_list.append(line)
        return path_list

    def path_list_2_file_level(self, level, path_list):
        print(str(level))
        file_level = self._FILELEVEL_LIST[level]
        with open(file_level, mode="w+") as fl:
            for line in path_list:
                try:
                    fl.write(line + "\n")
                except UnicodeEncodeError as e:
                    print(e.__str__())
                    print(str(line).encode('utf-8', 'surrogateescape').decode('ISO-8859-1'))

    def path_str_2_file_level(self, level, path_str):
        print(str(level))
        file_level = self._FILELEVEL_LIST[level]
        with open(file_level, mode="a+") as fl:
            try:
                fl.write(path_str + "\n")
            except UnicodeEncodeError as e:
                print(e.__str__())
                print(str(path_str).encode('utf-8', 'surrogateescape').decode('ISO-8859-1'))

    @staticmethod
    def __generate_file_level_name(level):
        file_level = 'LEVEL_' + str(level) + '-'
        file_level += ''.join(choice(ascii_uppercase + digits) for _ in range(6))
        return file_level

    def _main(self):
        for level in range(self.LEVEL):
            file_level = self.__generate_file_level_name(level)
            self._FILELEVEL_LIST.append(file_level)
            if level.__eq__(0):
                for path in self._get_path_content(self.BASE_DIR):
                    self.path_str_2_file_level(level, path)
            else:
                try:
                    with open(self._FILELEVEL_LIST[level - 1], mode="r") as dir_list:
                        for dir_str in dir_list:
                            for path in self._get_path_content(dir_str[:dir_str.find('\n')]):
                                self.path_str_2_file_level(level, path)
                except FileNotFoundError as e:
                    print("Fatal error.")
                    print(e.__str__())
                    pass
