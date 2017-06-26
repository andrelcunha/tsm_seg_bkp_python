#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""

from os import listdir, chdir
from os.path import join, isdir, islink, isfile
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
    def __path_str_2_file_level(file_level, path_str):
        with open(file_level, mode="a+") as fl:
            try:
                fl.write(path_str + "\n")
            except UnicodeEncodeError as e:
                print(e.__str__())
                new_str = deal_bad_string(path_str)
                print(new_str)
                fl.write(new_str + "\n")

    @staticmethod
    def __generate_file_level_name(level):
        file_level = 'LEVEL_' + str(level+1) + '-'
        file_level += ''.join(choice(ascii_uppercase + digits) for _ in range(6))
        return file_level

    def __main(self):
        for level in range(self.LEVEL):
            if level.__eq__(self._FILELEVEL_LIST.__len__()):
                dir_list = []
                if level.__eq__(0):
                    dir_list.extend([self.BASE_DIR+'\n'])
                else:
                    if isfile(self._FILELEVEL_LIST[level - 1]):
                        dir_list.extend(open(self._FILELEVEL_LIST[level - 1], mode="r"))
                    else:
                        print("file does not exists.")
                        self._FILELEVEL_LIST.pop(level - 1)
                        break
                if not dir_list:
                    print("dir_list is empty or does not exists at all")
                    break
                file_level = self.__generate_file_level_name(level)
                self._FILELEVEL_LIST.append(file_level)
                for dir_str in dir_list:
                    for path in get_path_content(dir_str[:dir_str.find('\n')]):
                        if not path:
                            print("empty")
                        else:
                            self.__path_str_2_file_level(file_level, path)


def get_path_content(parent_dir):
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
        return path_list


def deal_bad_string(bad_string):
    good_string = str(bad_string).encode('utf-8', 'surrogateescape').decode('ISO-8859-1')
    return good_string
