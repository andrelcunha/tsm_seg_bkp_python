#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
list file based on level.
"""
import string
from os import chdir, mkdir
from os.path import join
from random import choice, randrange

from tsm_seg_bkp.level_listdir import get_path_content

CHARLIST = '()+,-.;=@[]^_{}~ áéíóúàãõêüçÁÉÍÓÚÀÃÕÊÜÇ'


def generate_dir_tree(base: str, max_deep: int, max_files_per_dir=20, max_subdirs_per_dir=5):
    """

    :param base:
    :param max_deep:
    :param max_files_per_dir:
    :param max_subdirs_per_dir:
    :return:
    """
    root = join(base, __generate_dir_name())
    mkdir(root)
    print(root)
    parent_dir_content = [root]
    for deep in range(max_deep+1):
        tmp = []
        for path in parent_dir_content:
            print(path)
            generate_path_content(path, max_subdirs_per_dir, max_files_per_dir)
            tmp.extend(get_path_content(path))
        parent_dir_content = tmp


def __generate_file_name():
    """
    :return: generated filename
    """
    file_name = ''.join(choice(string.ascii_letters + string.digits + CHARLIST) for _ in range(randrange(4, 8)))
    file_name += '.'
    file_name += ''.join(choice(string.ascii_letters + string.digits) for _ in range(3))
    return file_name


def __generate_dir_name():
    """

    :return:
    """
    dir_name = ''.join(choice(string.ascii_letters + string.digits + CHARLIST) for _ in range(randrange(3, 8)))
    return dir_name


def generate_subdirs(max_subdirs_per_dir=5):
    """

    :return:
    """
    for i in range(randrange(2, max_subdirs_per_dir)):
        mkdir(__generate_dir_name())


def generate_files(max_files_per_dir=20):
    """

    :return:
    """
    for i in range(randrange(1, max_files_per_dir)):
        with open(__generate_dir_name(), mode="w") as file:
            txt = ''.join(choice(string.printable) for _ in range(randrange(1, 200)))
            file.write(txt)


def generate_path_content(path, max_files_per_dir=20, max_subdirs_per_dir=5):
        chdir(path)
        generate_files(max_files_per_dir)
        generate_subdirs(max_subdirs_per_dir)


