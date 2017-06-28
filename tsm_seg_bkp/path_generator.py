#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import os.path
import random
import string

from tsm_seg_bkp.level_listdir import get_path_content

# CHARLIST = '()+,-.;=@[]^_{}~ áéíóúàãõêüçÁÉÍÓÚÀÃÕÊÜÇ'
CHARLIST = '._^~ áéíóúàãõêüçÁÉÍÓÚÀÃÕÊÜÇ'


def generate_dir_tree(base: str, max_deep: int, random_qty=False, max_files_per_dir=20, max_subdirs_per_dir=5):
    """
    Create a directory tree for test purposes.
    HOW TO USE:
    :param base: int - Set the path where the first directory in the tree will be created.
    Make sure that you have write permission on that path.
    :param max_deep: int - Set the deep of the tree, meaning how much sublevels will be created.
    :param random_qty: (optional) boolean
    :param max_files_per_dir: int (optional)
    :param max_subdirs_per_dir: int (optional)

    """
    root = base
    parent_dir_content = [root]
    for deep in range(max_deep):
        tmp = []
        for path in parent_dir_content:
            print(path)
            generate_path_content(path, random_qty, max_files_per_dir, max_subdirs_per_dir)
            tmp.extend(get_path_content(path))
        parent_dir_content = tmp


def __generate_file_name():
    """
    :return: str - Generated filename
    """
    dot_ = random.randrange(1, 10)
    dot = ''
    if dot_ == 5:
        dot += '.'
    file_name = dot + ''.join(random.choice(string.ascii_letters + string.digits + CHARLIST)
                              for _ in range(random.randrange(4, 8)))
    file_name += '.'
    file_name += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
    return file_name


def __generate_dir_name():
    """

    :return: str - generated dirname
    """
    dir_name = ''.join(random.choice(string.ascii_letters + string.digits + CHARLIST)
                       for _ in range(random.randrange(3, 8)))
    return dir_name


def generate_subdirs(random_qty=False, max_subdirs_per_dir=5):
    """

    :return: None
    """
    if random_qty:
        _range = random.randrange(1, max_subdirs_per_dir)
    else:
        _range = max_subdirs_per_dir
    for i in range(_range):
        try:
            os.mkdir(__generate_dir_name())
        except FileExistsError:
            pass


def generate_files(random_qty=False, max_files_per_dir=20):
    """
    Generates a number of files whith randomic names
    :param random_qty:
    :param max_files_per_dir:
    :return: None
    """
    if random_qty:
        _range = random.randrange(1, max_files_per_dir)
    else:
        _range = max_files_per_dir
    for i in range(_range):
        with open(__generate_dir_name(), mode="w") as file:
            txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, ' \
                  'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
            file.write(txt)


def generate_path_content(path, random_qty=False, max_files_per_dir=20, max_subdirs_per_dir=5):
    os.chdir(path)
    generate_files(random_qty, max_files_per_dir)
    generate_subdirs(random_qty, max_subdirs_per_dir)


if __name__ == '__main__':
    base = "/tmp/path_generator"
    max_deep = 5
    generate_dir_tree(base, max_deep)
