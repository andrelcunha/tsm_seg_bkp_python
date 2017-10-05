#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Este módulo permite listar o conteúdo dos diretórios, de modo que é possível escolher até que nível se deseja listar.
Ele é essencial para o funcionamento do módulo
__Modo de usar__:
    Caso se deseje usar de modo 'stand alone', basta executar:
        python3 -m tsm_seg_bkp.level_listdir <caminho-a-ser-listado> <numero-de-niveis>, onde:
            - caminho-a-ser-listado é o caminho que se deseja listar.
            - numero-de-niveis é a quantidade de niveis que se deseja listar.
    Quando executado no modo 'stand alone', os conteúdos são mostrados na saída padrão ou consultados via sistema de ar-
    quivos, geralmente no caminho /tmp/. O nome do diretório temporário, TMP_DIR, é formado pelo prefixo+ANO+MES+DIA+
    HORA+MINUTO+SEGUNDO.

"""

from os import chdir, scandir, mkdir
from os.path import join, isdir, isfile, abspath
from tempfile import TemporaryDirectory


class LevelListDir:
    """
    Esta classe tem alguns nomes chave:
    BASE_DIR é o diretório base, informado no início da execução
    LEVEL é o nível, podendo se referir ao nível atual da execução ou ao nível configurado inicialmente.
    FILELEVEL_LIST é uma lista contendo nomes de arquivos que armazenam os diretórios listados.
    A idéia de se listar em um arquivo em vez de usar a memória é poupar recursos em situações onde o consumo é crítico.
    TMP_DIR é um diretório temporário onde os arquivos 'filelevel' são gravados. O parâmetro 'prefix' é um prefixo dado
    ao diretório para que o mesmo se destaque.
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
        Adiciona um caminho listado ao arquivo.
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
        """
        Gera o nome do arquivo que conterá os diretórios listados. Tal nome é baseado no nível (lvl) em que está a execu-
        ção.
        :param lvl:
        :return:
        """
        file_level = 'LEVEL_' + str(lvl+1)
        return file_level

    def __main(self):
        """
        Esta é a parte principal do módulo. É separado do __main__ para que possa ser usado incorporado a outro módulo,
        como bkp_nas_seg.
        :return:
        """
        for lvl in range(self.LEVEL):
            print("nivel {lvl}".format(lvl=(str(lvl))))
            if lvl.__eq__(self._FILELEVEL_LIST.__len__()):
                # print("lvl={size}".format(size=str(self._FILELEVEL_LIST.__len__())))
                dir_list = []
                file_lvl = self.__generate_file_level_name(lvl)
                if lvl.__eq__(0):
                    if type(self.BASE_DIR) is str:
                        dir_list.extend([self.BASE_DIR + '\n'])
                    else:
                        for base_dir in self.BASE_DIR:
                            dir_list.extend([base_dir + '\n'])
                    for line in dir_list:
                        line = prepare_line(line)
                        #print(line)
                        # for path in timeout(get_path_content, (line,), timeout_duration=30000000, default=line):
                        for path in get_path_content(line):
                            if not path:
                                print("empty")
                            else:
                                print(path)
                                self.__path_str_2_file_level(file_lvl, path)
                else:
                    if isfile(self._FILELEVEL_LIST[lvl - 1]):
                        with open(self._FILELEVEL_LIST[lvl - 1], mode="r") as former_file_lvl:
                            for line in former_file_lvl:
                                line = prepare_line(line)
                                #print(line)
                                for path in get_path_content(line):
                                    if not path:
                                        print("empty")
                                    else:
                                        print(path)
                                        self.__path_str_2_file_level(file_lvl, path)
                    else:
                        print("Reached the deepest level.")
                        self._FILELEVEL_LIST.pop(lvl - 1)
                        break
                self._FILELEVEL_LIST.append(file_lvl)

    def get_levellist(self):
        result = []
        for filename in self._FILELEVEL_LIST:
            result.append(join(self.TMP_DIR.name, filename))
        return result


def prepare_line(line):
    """
    Remove a quebra de linha (\n) de cada linha lida do arquivo.
    :param line:
    :return:
    """
    return line[:line.find('\n')]


def timeout(func, args=(), kwargs={}, timeout_duration=3600, default=None):
    """
    Função com intenção de dar continuidade à execução, caso um diretório específico demore muito (timeout_duration).
    Atualmente não está funcional, pois pode haver bugs.
    :param func:
    :param args:
    :param kwargs:
    :param timeout_duration:
    :param default:
    :return:
    """
    import signal

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError:
        result = default
    finally:
        signal.alarm(0)

    return result


def get_path_content(directory):
    """
    Lista o conteúdo de um diretório e o retorna como objeto list.
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
    """
    Função com o objetivo de lidar com strings que contém caracteres especiais.
    :param bad_string:
    :return:
    """
    good_string = str(bad_string).encode('utf-8', 'surrogateescape').decode('ISO-8859-1')
    return good_string

if __name__ == '__main__':
    import sys
    import shutil
    from tsm_seg_bkp.tools import create_timestamp
    parent_dir = ''
    level = 0
    try:
        parent_dir = sys.argv[1]
        try:
            level = int(sys.argv[2])
        except ValueError:
            print('Invalid argument: Expecting integer, received char.')

    except IndexError as ie:
        print(str(ie))
        print("Missing arguments. Expecting 2, received {argv}.".format(argv=(len(sys.argv)-1)))
        exit(1)
    if not isdir(parent_dir):
        print("File not found.")
    lld = LevelListDir(abspath(parent_dir), level)
    ts = create_timestamp()
    dirname= "level_listdir_" + ts
    tmp_dir = join("/tmp/", dirname)
    mkdir(tmp_dir)
    for level, file in enumerate(lld.get_levellist()):
        level_file = "level_" + str(level)
        try:
            shutil.copy2(join(parent_dir, file), join(tmp_dir, level_file))
        except FileNotFoundError:
            print("No more levels.")
    chdir("/")
    exit(0)
