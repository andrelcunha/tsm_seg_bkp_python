#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
TODO
"""
# import _thread
import time


def generate_config_file(file_name, nodename='__MYNODE__'):
    """

    :param config_file:
    :return:
    """
    config_content = '{\n' \
                     '"PROCS": 30,\n' \
                     '"LEVEL_THRESHOLD": 3,\n' \
                     '"LEVEL_MAXLIMIT": 5,\n' \
                     '"BASE_DIR": "",\n' \
                     '"NODENAME": [""],\n' \
                     '"OPTFILE": "",\n' \
                     '"TSM_DIR": "",\n' \
                     '"TSM_LOG_DIR": "",\n' \
                     '"TMP_DIR": "",\n' \
                     '"DSMC": "",\n' \
                     '"VERBOSE": False\n' \
                     '}'
    variables={'nodename': nodename}

    with open(file_name, mode="w") as fn:
        fn.write(config_content.format_map(variables))
    return None


if __name__ == "__main__":
    import sys
    import os.path
    # conf_file = ''
    start = time.time()
    try:

        # conf_file = sys.argv[1]
        node_name = sys.argv[1]
    except IndexError as ie:
        print(str(ie))
        print("Missing arguments. Expecting 2, received {argv}.".format(argv=(len(sys.argv)-1)))
        conf_file = "config.json"
    if not os.path.isfile(conf_file):
        print("Configuration file not found.\n")
        generate_config_file(conf_file)
        print("Configuration file example generated.")
        print("Please, configure with your needs and try again.")
        exit(0)
    else:
        print("Found configuration file.\n")
    exit(0)

