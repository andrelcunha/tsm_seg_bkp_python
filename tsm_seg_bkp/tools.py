

def create_timestamp():
    import datetime
    return '{:%Y%m%d.%H%M%S}'.format(datetime.datetime.now())


def humanize_time(secs):
    days = int(secs // 86400)
    hours = int(secs // 3600 % 24)
    minutes = int(secs // 60 % 60)
    seconds = int(secs % 60)
    return days, hours, minutes, seconds


def file_len(fname):
    """
    Get the number of lines of a file.
    Retorna o numero de linhas de um arquivo
    :param fname: Name of file (str)
    :return: number of lines of fname
    """
    import os
    size = os.stat(fname).st_size
    if size > 0:
        with open(fname) as f:
            i = 0
            for i, l in enumerate(f):
                pass
        return i + 1
    else:
        return 0


def make_sure_path_exists(path):
    """
    Verify if path exists and create it otherwise
    :param: path: Path that will be checked.
    :return: None
    """
    import errno
    import os
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return None


def make_sure_file_exists(file_name):
    """
    Verify if file exists and create it otherwise
    :param: file_name: Name of file that will be checked.
    :return: None
    """
    import os
    if os.path.isfile(file_name):
        fn = open(file_name, mode="w")
        fn.write('')
        fn.close()
    return None


def writeonfile(file_name, message):
    """
    Write a message on file.
    :param: file_name: Name of file that will receives the message.
    :param: message: messege that will be appended into file.
    """
    my_file = open(file_name, mode="a+")
    my_file.write(message)
    my_file.close()
    return None


def writeonfilebytes(file_name, byte_content):
    """
    Write bytes on file.
    :param: file_name: Name of file that will receives the message.
    :param: message: messege that will be appended into file.
    """
    my_file = open(file_name, mode="ab")
    my_file.write(byte_content)
    my_file.close()
    return None


def file_len(fname):
    """
    Get the number of lines of a file.
    Retorna o numero de linhas de um arquivo
    :param fname: Name of file (str)
    :return: number of lines of fname
    """
    import os
    size = os.stat(fname).st_size
    if size > 0:
        with open(fname) as f:
            i = 0
            for i, l in enumerate(f):
                pass
        return i + 1
    else:
        return 0
