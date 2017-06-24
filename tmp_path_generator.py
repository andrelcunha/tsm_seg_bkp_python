#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""
import string
from os import listdir, chdir, makedirs
from os.path import join, isdir, isfile
from random import choice, randrange


class TmpPathGenerator:
    """
    I do not know yet.
    """

    def __init__(self, base_dir='/tmp', deep=10):
        self.BASE_DIR = base_dir
        self.DEEP = deep
        self._FILELEVEL_LIST = []
        # self.TMP_DIR = TemporaryDirectory(prefix="bkp_seg_python_")
        # chdir(self.TMP_DIR.name)
        chdir(self.BASE_DIR)
        # self._main()

    @staticmethod
    def _get_path_content(parent_dir):
        """
        Get the content (directories) of a single path.
        :param parent_dir:
        :return:
        """
        path_list = []
        try:
            path_list = [join(parent_dir, d) for d in listdir(parent_dir) if isdir(join(parent_dir, d))]
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
        file_level = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(6))
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
                fl.write(line + "\n")

    @staticmethod
    def __generate_file_name():
        """

        :return:
        """
        charlist = '!#$&()+,-.;=@[]^_`{}~ áéíóúàãõêüçÁÉÍÓÚÀÃÕÊÜÇ'
        file_name = ''.join(choice(string.ascii_letters + string.digits + charlist) for _ in range(randrange(4, 8)))
        file_name += '.'
        file_name += ''.join(choice(string.ascii_letters + string.digits) for _ in range(3))
        return file_name

    @staticmethod
    def __generate_dir_name():
        """

        :return:
        """
        charlist = '!#$&()+,-.;=@[]^_`{}~ áéíóúàãõêüçÁÉÍÓÚÀÃÕÊÜÇ'
        dir_name = ''.join(choice(string.ascii_letters + string.digits + charlist) for _ in range(randrange(3, 8)))
        return dir_name

    def __generate_subdirs(self):
        """

        :return:
        """
        for i in range(randrange(2, 5)):
            makedirs(self.__generate_dir_name())

    def __generate_files(self):
        """

        :return:
        """
        for i in range(randrange(1, 20)):
            with open(self.__generate_dir_name(), mode="w") as file:
                txt = ''.join(choice(string.printable) for _ in range(randrange(1, 200)))
                file.write(txt)

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
                    for path in self.__get_path_content(dir_str[:dir_str.find('\n')]):
                        if not path:
                            print("empty")
                        else:
                            self.__path_str_2_file_level(file_level, path)
