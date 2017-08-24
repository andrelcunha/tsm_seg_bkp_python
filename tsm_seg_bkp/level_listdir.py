#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""

from os import chdir, scandir
from os.path import join, isdir, isfile
from tempfile import TemporaryDirectory
# from random import choice
# from string import ascii_uppercase, digits


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
        """
        Appends a path into file.
        :param file_level:
        :param path_str:
        :return:
        """
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
        file_level = 'LEVEL_' + str(lvl+1)
        return file_level

    def __main(self):
        for lvl in range(self.LEVEL):
            print("nivel {lvl}".format(lvl=(str(lvl))))
            if lvl.__eq__(self._FILELEVEL_LIST.__len__()):
                print("lvl={size}".format(size=str(self._FILELEVEL_LIST.__len__())))
                dir_list = []
                file_lvl = self.__generate_file_level_name(lvl)
                if lvl.__eq__(0):
                    dir_list.extend([self.BASE_DIR+'\n'])
                    for line in dir_list:
                        for path in get_path_content(line[:line.find('\n')]):
                            if not path:
                                print("empty")
                            else:
                                self.__path_str_2_file_level(file_lvl, path)
                else:
                    if isfile(self._FILELEVEL_LIST[lvl - 1]):
                        with open(self._FILELEVEL_LIST[lvl - 1], mode="r") as former_file_lvl:
                            for line in former_file_lvl:
                                # dir_list.append(line)
                                for path in get_path_content(line[:line.find('\n')]):
                                    if not path:
                                        print("empty")
                                    else:
                                        print(path)
                                        self.__path_str_2_file_level(file_lvl, path)
                    else:
                        print("file does not exists.")
                        self._FILELEVEL_LIST.pop(lvl - 1)
                        break
                self._FILELEVEL_LIST.append(file_lvl)

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
        # print(directory)
        for entry in scandir(directory):
            if entry.is_dir(follow_symlinks=False):
                path_list.append(entry.path)
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
