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
    :param base_dir: string -- path to be listed.
    :param lvl: int -- maximum deep that the script will dive into.
    """
    def __init__(self, base_dir, lvl=0):
        self.BASE_DIR = base_dir
        self.LEVEL = lvl
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
    def __generate_file_level_name(lvl):
        file_level = 'LEVEL_' + str(lvl+1) + '-'
        file_level += ''.join(choice(ascii_uppercase + digits) for _ in range(6))
        return file_level

    def __main(self):
        for lvl in range(self.LEVEL):
            if lvl.__eq__(self._FILELEVEL_LIST.__len__()):
                dir_list = []
                if lvl.__eq__(0):
                    dir_list.extend([self.BASE_DIR+'\n'])
                else:
                    if isfile(self._FILELEVEL_LIST[lvl - 1]):
                        dir_list.extend(open(self._FILELEVEL_LIST[lvl - 1], mode="r"))
                    else:
                        print("file does not exists.")
                        self._FILELEVEL_LIST.pop(lvl - 1)
                        break
                if not dir_list:
                    print("dir_list is empty or does not exists at all")
                    break
                file_lvl = self. __generate_file_level_name(lvl)
                self._FILELEVEL_LIST.append(file_lvl)
                for dir_str in dir_list:
                    for path in get_path_content(dir_str[:dir_str.find('\n')]):
                        if not path:
                            print("empty")
                        else:
                            self.__path_str_2_file_level(file_lvl, path)

    def get_levellist(self):
        result = []
        for filename in self._FILELEVEL_LIST:
            result.append(join(self.TMP_DIR.name, filename))
        return result


def get_path_content(directory):
    """
    Get the content (directories) of a single path.
    :param directory:
    :return:
    """
    path_list = []
    try:
        for d in listdir(directory):
            dir_name = join(directory, d)
            if isdir(dir_name):
                if not islink(dir_name):
                    path_list.append(dir_name)
    except PermissionError as pe:
        print(str(pe))
    except FileNotFoundError as fnfe:
        print(str(fnfe))
    finally:
        return path_list


def deal_bad_string(bad_string):
    good_string = str(bad_string).encode('utf-8', 'surrogateescape').decode('ISO-8859-1')
    return good_string

if __name__ == '__main__':
    import sys
    import shutil
    parent_dir = ''
    level = 0
    try:
        parent_dir = sys.argv[1]
        level = int(sys.argv[2])
    except IndexError as ie:
        print(str(ie))
        print("Missing arguments. Expecting 2, received {argv}.".format(argv=(len(sys.argv)-1)))
        exit(1)
    if not isdir(parent_dir):
        print("File not found.")
    lld = LevelListDir(parent_dir, level)
    for level, file in enumerate(lld.get_levellist()):
        level_file = "level_" + str(level)
        shutil.copy2(join(parent_dir, file), join("/tmp/", level_file))
    chdir("/")
    exit(0)
