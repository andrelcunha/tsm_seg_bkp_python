#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Executes a segmented backup from target path, setup in BASE_DIR attribute.
"""

import _thread
import errno
import json
import os
import os.path
import time
from subprocess import Popen, PIPE
from tempfile import TemporaryFile

import tsm_seg_bkp.level_listdir


class BkpNasSeg:
    """
    Executes a segmented backup from target path, setup in BASE_DIR attribute.
    """
    PROCS = 0
    LEVEL_THRESHOLD = 0
    LEVEL_MAXLIMIT = 0
    BASE_DIR = ""
    NODENAME = ""
    OPTFILE = ""
    TSM_DIR = ""
    TSM_LOG_DIR = ""
    TMP_DIR = ""
    DSMC = ""
    TXT_DIR = ""
    NOMEDIR = ""
    FILENODE = ""
    TSMSCHEDLOG = ""
    TSMERRORLOG = ""
    PID_CONTROL = []
    debug = True

    def __init__(self, config_file):
        self.set_configuration(self.get_configuration(config_file))
        self.NOMEDIR = self.BASE_DIR.replace("/", "")
        self.TXT_DIR = os.path.join(self.TSM_DIR, "TXT")
        self.FILENODE = os.path.join(self.TXT_DIR, self.NODENAME + "-" + self.NOMEDIR + ".txt")
        self.TSMSCHEDLOG = os.path.join(self.TSM_LOG_DIR, "dsmsched-" + self.NODENAME + ".log")
        self.TSMERRORLOG = os.path.join(self.TSM_LOG_DIR, "dsmerror-" + self.NODENAME + ".log")
        self.PID_CONTROL = []
        self.make_sure_path_exists(self.TXT_DIR)
        self.make_sure_file_exists(self.FILENODE)
        if self.debug:
            for attrib in dir(self):
                print("{0}: {1}".format(attrib, getattr(self, attrib)))

    @staticmethod
    def config_file_exists(config_file):
        return not os.path.isfile(config_file)

    @staticmethod
    def get_configuration(config_file):
        """
        Get configuration from config file
        :return: json
        """

        with open(config_file) as json_data:
            config = json.load(json_data)
        return config

    def set_configuration(self, config):
        """
        Set configuration values to their attributes.
        :param config: json
        :return:
        """
        for attrib in dir(self):
            if config.__contains__(attrib):
                setattr(self, attrib, config[attrib])

    @staticmethod
    def make_sure_path_exists(path):
        """
        Verify if path exists and create it otherwise
        :param: path: Path that will be checked.
        :return: None
        """
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        return None

    @staticmethod
    def make_sure_file_exists(file_name):
        """
        Verify if file exists and create it otherwise
        :param: file_name: Name of file that will be checked.
        :return: None
        """
        if os.path.isfile(file_name):
            fn = open(file_name, mode="w")
            fn.write('')
            fn.close()
        return None

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def testlevel(level_threshold, level_max):
        """
        Test 'level' configuration. Unnecessery by now.
        Testa configuração de 'nivel'
        :param: None
        :return: flag_ok: Boolean"""
        return (0 < level_max < 6) and (level_threshold <= level_max) and (level_threshold > 0)

    def generatetextfile(self):
        """
        Generate text file with all directories that will be backed up,
        including sub=yes or sub=no option on each line.

        Geração do arquivo texto com todos os diretórios que sofrerão backup,
        incluíndo a opção de sub=yes ou sub=no em cada linha.
        :param: None
        :return None
        """

        file_level_list = []
        lld = tsm_seg_bkp.level_listdir.LevelListDir(self.BASE_DIR, self.LEVEL_MAXLIMIT)
        file_level_list.extend(lld.get_levellist())
        for level in range(1, self.LEVEL_MAXLIMIT + 1):
            if level.__le__(self.LEVEL_THRESHOLD):
                file_level = file_level_list[level - 1]
                if level.__lt__(self.LEVEL_THRESHOLD):
                    cmd = "sed 's/^/-sub=no \"/' " + file_level + " >> " + self.FILENODE
                    os.system(cmd)
                elif level.__eq__(self.LEVEL_THRESHOLD):
                    cmd = "sed 's/^/-sub=yes \"/' " + file_level + " >> " + self.FILENODE
                    os.system(cmd)
        file_list = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-LISTADIR.txt"
        cmd = "sed \"/.snapshot/d\" " + self.FILENODE + ">> " + file_list
        '''
        this statement can be replaced by str.replace(".snapshot","")
        '''
        os.system(cmd)
        cmd = "sed 's/$/\/\"/' " + file_list + ">" + self.FILENODE
        os.system(cmd)
        cmd = "rm -f " + file_list
        os.system(cmd)
        return None

    @staticmethod
    def file_len(fname):
        """
        Get the number of lines of a file.
        Retorna o numero de linhas de um arquivo
        :param fname: Name of file (str)
        :return: number of lines of fname
        """

        size = os.stat(fname).st_size
        if size > 0:
            with open(fname) as f:
                i = 0
                for i, l in enumerate(f):
                    pass
            return i + 1
        else:
            return 0

    def dsmcdecrementa(self, command, file_out, file_err, sudo=False, debug=False):
        """
        Executa backups incrementais em paralelo, para as primeiras $PROCS linhas do arquivo de diretórios.
        Depois exclui estas linhas da lista de diretórios, e decrementa a váriavel de contabilização do número de linhas
        ($LINHAS).
        """
        date = time.strftime("%d%m%y-%H%M%S")
        # file_node_ciclo = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-CICLO-" + date
        file_node_ciclo = os.path.join(self.TXT_DIR, self.NODENAME)
        file_node_ciclo += "-" + self.NOMEDIR + "-CICLO-" + date + ".txt"
        self.writeonfile(file_node_ciclo, self.pop_out_n_lines(self.FILENODE, self.PROCS))
        while self.file_len(file_node_ciclo) > 0:
            tmp = self.pop_out_n_lines(file_node_ciclo, 1)
            dir_target = tmp.replace('\n', '')
            param_sub, param_target = self.split_target_str(dir_target, debug)
            optfile = self.OPTFILE
            cmd = self.prepare_command(command, param_sub, param_target, optfile, sudo, debug)
            secs = 1
            while self.PID_CONTROL.__len__().__gt__(self.PROCS):
                time.sleep(secs)
                secs *= 2
                self.execute_command(cmd, file_out, file_err, debug)
        return None

    @staticmethod
    def split_target_str(target_str, debug=False):
        """
        Slipt string with target directory into parm_dir and param_sub
        :param target_str:
        :param debug:
        :return: tuple param_sub, param_target
        """
        param_sub = ""
        param_target = ""
        try:
            # separa param '-sub=yes' do caminho alvo
            param_sub, param_target = target_str.split(' ', 1)
            if debug:
                print('"' + param_target + '"')
        except ValueError:
            print("Error: not enough values to unpack")
            print(target_str)
            exit(-1)
        return param_sub, param_target

    @staticmethod
    def prepare_command(command, param_sub, param_target, optfile, sudo=False, debug=False):
        """
        Prepare the backup command
        :param command: base command to be executed i.e: /usr/bin/dsmc
        :param param_sub:
        :param param_target:
        :param optfile:
        :param sudo:
        :param debug:
        :return: string cmd
        """
        cmd = []
        if sudo:
            cmd.extend(["sudo"])
        cmd.extend([command])
        cmd.extend(["i"])
        cmd.extend(["-verbose"])
        cmd.extend(["-optfile=" + optfile])
        cmd.extend([param_sub])
        cmd.extend([param_target])
        if debug:
            print(cmd)
        return cmd

    def execute_command(self, cmd, file_out, file_err, debug=False):
        """
        Execute TSM backup of target path.
        :param cmd: list
        :param file_out:
        :param file_err:
        :param debug:
        :return:
        """
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        self.PID_CONTROL.append(proc.pid)
        outs, errs = proc.communicate()
        self.writeonfilebytes(file_out, outs)
        self.writeonfilebytes(file_err, errs)
        proc.wait()
        if proc.poll() is not None:
            if debug:
                print("PID {PID} done.".format(PID=proc.pid))
            self.PID_CONTROL.remove(proc.pid)
        return None

    @staticmethod
    def pop_out_n_lines(input_file, lines):
        """
        Pop out N first lines from input file.
        :param input_file: file with n lines to pop out.
        :param lines: number of lines to pop out.
        :return: String with n first lines
        """
        fst_lines = ""
        tmp_file = TemporaryFile(mode="w+")
        inputf = open(input_file)
        for i, line in enumerate(inputf):
            if i < lines:
                fst_lines += line
            else:
                tmp_file.write(line)
        inputf.close()
        tmp_file.seek(0)
        with open(input_file, mode="w+") as inputf:
            for line in tmp_file:
                inputf.write(line)
        tmp_file.close()
        return fst_lines


def generate_config_file(config_file):
    """TODO"""
    config_content = '{\n' \
                     '"PROCS": 30,\n' \
                     '"LEVEL_THRESHOLD": 3,\n' \
                     '"LEVEL_MAXLIMIT": 5,\n' \
                     '"BASE_DIR": "/home",\n' \
                     '"NODENAME": "TESTE_CUNHA",\n' \
                     '"OPTFILE": "/opt/tivoli/tsm/client/ba/bin/dsm.opt",\n' \
                     '"TSM_DIR": "/opt/tivoli/tsm/client/ba/bin",\n' \
                     '"TSM_LOG_DIR": "/opt/tivoli/tsm/client/ba/bin/logs",\n' \
                     '"TMP_DIR": "/tmp/tsm_seg_bkp/",\n' \
                     '"DSMC": "/usr/bin/dsmc"\n' \
                     '}'
    with open(config_file, mode="w") as cf:
        cf.write(config_content)


def main(config_file):
    """
    Main
    :return:
    """
    bkp = BkpNasSeg(config_file)
    if not bkp.testlevel(bkp.LEVEL_THRESHOLD, bkp.LEVEL_MAXLIMIT):
        msg = "Nível máximo de segmentação devem estar entre um (1) e cinco (5).\n"
        msg += "Valor de corte para ativar backup em subniveis deve ser menor que nível máximo.\n"
        msg += "Programa terminado."
        print(msg)
        exit(-1)
    bkp.generatetextfile()
    linhas = bkp.file_len(bkp.FILENODE)
    print("Initial quatity of files to be copied: {linhas}".format(linhas=linhas))
    threads = 0
    # enquanto tiver arquivos a serem copiados
    file_out = bkp.TSMSCHEDLOG
    file_err = bkp.TSMERRORLOG
    os.chdir(bkp.TSM_DIR)
    while True:
        try:
            # bkp.dsmcdecrementa()
            _thread.start_new_thread(bkp.dsmcdecrementa, (file_out, file_err))
            threads += 1
        except RuntimeError:
            print("Error: unable to start thread")
        finally:
            linhas = bkp.file_len(bkp.FILENODE)
            if bkp.debug:
                print("thread " + str(threads))
                print("Files to be copied: {linhas}".format(linhas=linhas))
            time.sleep(0.1)
            for pid in bkp.PID_CONTROL:
                if bkp.debug:
                    print(str(pid))
            if bkp.debug:
                print("Total ative processes: " + str(bkp.PID_CONTROL.__len__()))
        if (not bkp.PID_CONTROL) and linhas == 0:
            break
    return 0


if __name__ == "__main__":
    import sys
    import os.path
    conf_file = ''
    try:
        conf_file = sys.argv[1]
    except IndexError as ie:
        print(str(ie))
        print("Missing arguments. Expecting 1, received {argv}.".format(argv=(len(sys.argv)-1)))
        conf_file = "config.json"
        if not os.path.isfile(conf_file):
            print("Configuration file not found.\n")
            generate_config_file(conf_file)
            print("Configuration file example generated.")
            print("Please, configure with your needs and try again.")
            exit(0)
        else:
            print("Found configuration file.\n")
    try:
        if not os.path.isfile(conf_file):
            raise FileNotFoundError
        main(conf_file)
    except FileNotFoundError as fnfe:
        print(str(fnfe))
        print("File not found. Please inform a existent path.")
        exit(1)
