#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""

from os import listdir, chdir
from os.path import join, isdir, islink
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
        self.__main()

    @staticmethod
    def __get_path_content(parent_dir):
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
                    if not islink(dir_name):
                        path_list.append(dir_name)
        except PermissionError as e:
            print(str(e))
        except FileNotFoundError as e:
            print(str(e))
        finally:
            if not path_list:
                return None
            else:
                return path_list

    '''
    def __get_level_path_list(self, parent_dir_list):
        """
        Get a list of directories in a level directory and lists the sub dirs on each dir.
        In the end, returns a list of all the next sublevel
        :param parent_dir_list:
        :return:
        """
        path_list = []
        for parent_dir in parent_dir_list:
            path_list.extend(self.__get_path_content(parent_dir))
        return path_list
    '''

    '''
    @staticmethod
    def __persist_path_list(path_list, level):
        file_level = ''.join(choice(ascii_uppercase + digits) for _ in range(6))
        file_level += 'TMP_LEVEL_' + str(level)
        with open(file_level, mode="w") as fl:
            for line in path_list:
                fl.write(line)
        return file_level
    '''

    def __file_level_2_path_list(self, level):
        print(str(level))
        path_list = []
        file_level = self._FILELEVEL_LIST[level]
        with open(file_level, mode="r") as fll:
            for line in fll:
                path_list.append(line)
        return path_list

    def __path_list_2_file_level(self, level, path_list):
        print(str(level))
        file_level = self._FILELEVEL_LIST[level]
        with open(file_level, mode="w+") as fl:
            for line in path_list:
                try:
                    fl.write(line + "\n")
                except UnicodeEncodeError as e:
                    print(e.__str__())
                    print(str(line).encode('utf-8', 'surrogateescape').decode('ISO-8859-1'))

    def __path_str_2_file_level(self, level, path_str):
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

    def __main(self):
        flag_done = False
        for level in range(self.LEVEL):
            if flag_done:
                break
            else:
                file_level = self.__generate_file_level_name(level)
                self._FILELEVEL_LIST.append(file_level)
                if level.__eq__(0):
                    content = self.__get_path_content(self.BASE_DIR)
                    if not content:
                        for path in content:
                            self.__path_str_2_file_level(level, path)
                    else:
                        self._FILELEVEL_LIST.remove(file_level)
                        flag_done = True
                        break
                else:
                    try:
                        with open(self._FILELEVEL_LIST[level - 1], mode="r") as dir_list:
                            for dir_str in dir_list:
                                content = self.__get_path_content(dir_str[:dir_str.find('\n')])
                                if not content:
                                    for path in content:
                                        self.__path_str_2_file_level(level, path)
                                else:
                                    self._FILELEVEL_LIST.remove(file_level)
                                    flag_done = True
                                    break
                    except FileNotFoundError as e:
                        print("Fatal error.")
                        print(e.__str__())
                        break

    def get_filelevel(self, level):
        if level.__gt__(0) and level.__lt__(self._FILELEVEL_LIST.__len__() + 1):
            return self._FILELEVEL_LIST[level - 1]
        else:
            print("List index out of bounds.")
            exit(code=1)
