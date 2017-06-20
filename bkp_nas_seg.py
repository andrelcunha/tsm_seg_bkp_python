#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Executes a segmented backup from target path, setup in BASE_DIR attribute.
"""

import _thread
import errno
import json
import os
import subprocess
import tempfile
import time


class BkpNasSeg:
    """
    Executes a segmented backup from target path, setup in BASE_DIR attribute.
    """
    PROCS = 0
    LEVELS = 0
    LEVEL_THRESHOULD = 0
    BASE_DIR = ""
    NODENAME = ""
    TSM_DIR = ""
    TMP_DIR = ""
    DSMC = ""
    TXT_DIR = ""
    NOMEDIR = ""
    FILENODE = ""
    TSMSCHEDLOG = ""
    TSMERRORLOG = ""
    PID_CONTROL = []
    DATE = time.strftime("%d%m%y-%H%M%S")
    debug = True

    def __init__(self):
        self.set_configuration(self.get_configuration())
        self.NOMEDIR = self.BASE_DIR.replace("/", "")
        self.TXT_DIR = self.TSM_DIR + "/TXT"
        self.FILENODE = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + ".txt"
        self.TSMSCHEDLOG = self.TSM_DIR + "/logs/dsmsched-" + self.NODENAME + ".log"
        self.TSMERRORLOG = self.TSM_DIR + "/logs/dsmerror-" + self.NODENAME + ".log"
        self.PID_CONTROL = []
        self.make_sure_path_exists(self.TXT_DIR)
        self.make_sure_file_exists(self.FILENODE)
        if self.debug:
            for attrib in dir(self):
                print("{0}: {1}".format(attrib, getattr(self, attrib)))

    @staticmethod
    def get_configuration():
        """
        Get configuration from config file
        :return: json
        """
        cwd = os.path.realpath(__file__)
        cwd = cwd[:cwd.find(os.path.basename(__file__))]
        with open(cwd + '/config.json') as json_data:
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

    def testlevel(self):
        """
        Test 'level' configuration. Unnecessery by now.
        Testa configuração de 'nivel'
        :param: None
        :return: flag_ok: Boolean"""
        msg = "Níveis de segmentação devem estar entre um (1) e cinco (5)"
        flag_ok = True
        if self.LEVELS < 1 or self.LEVELS > self.LEVEL_THRESHOULD:
            self.writeonfile(self.TSMSCHEDLOG, msg)
            self.writeonfile(self.TSMERRORLOG, msg)
            flag_ok = False
        return flag_ok

    def generatetextfile(self):
        """
        Generate text file with all directories that will be backed up,
        including sub=yes or sub=no option on each line.

        Geração do arquivo texto com todos os diretórios que sofrerão backup,
        incluíndo a opção de sub=yes ou sub=no em cada linha.
        :param: None
        :return None
        """
        for level in range(1, 5):
            if level.__lt__(self.LEVELS):
                file_level = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-NIVEL" + str(level) + ".txt"
                aux = "*/"
                cmd = "ls -1 -d " + self.BASE_DIR + "/"
                cmd += level * aux
                cmd += " > " + file_level
                os.system(cmd)
                # cmd content reset after execution
                cmd = "sed 's/^/-sub=no \"/' " + file_level + " >> " + self.FILENODE
                os.system(cmd)
                cmd = "rm -f " + file_level
                os.system(cmd)
            if level.__eq__(self.LEVELS):
                file_level = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-NIVEL" + str(level) + ".txt"
                aux = "*/"
                cmd = "ls -1 -d " + self.BASE_DIR + "/"
                cmd += level * aux
                cmd += " > " + file_level
                os.system(cmd)  # cmd content reset after execution
                cmd = "sed 's/^/-sub=yes \"/' " + file_level + " >> " + self.FILENODE
                os.system(cmd)
                cmd = "rm -f " + file_level
                os.system(cmd)
        file_list = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-LISTADIR.txt"
        cmd = "sed \"/.snapshot/d\" " + self.FILENODE + ">> " + file_list
        os.system(cmd)
        cmd = "sed 's/$/\"/' " + file_list + ">" + self.FILENODE
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

    def dsmcdecrementa_fake(self, threadname):
        """
        Do not use it. Method created just for test purposes.
        :param threadname:
        :return: None
        """
        count = 0
        file0 = self.FILENODE
        file1 = self.FILENODE+".tmp"
        while count < 5:
            time.sleep(10)
            count += 1
            tmp = self.pop_out_n_lines(file0, 1)
            cmd = "mv " + file1 + " " + file0
            os.system(cmd)
            print("{0} - {1}: {2}".format(threadname, count, tmp))
        return None

    def dsmcdecrementa(self):
        """
        Executa backups incrementais em paralelo, para as primeiras $PROCS linhas do arquivo de diretórios.
        Depois exclui estas linhas da lista de diretórios, e decrementa a várial de contabilização do número de linhas
        ($LINHAS).
        """
        file_node_ciclo = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-CICLO-"+self.DATE
        file_node_ciclo += ".txt"
        self.writeonfile(file_node_ciclo, self.pop_out_n_lines(self.FILENODE, self.PROCS))
        while self.file_len(file_node_ciclo) > 0:
            tmp = self.pop_out_n_lines(file_node_ciclo, 1)
            dir_target = tmp[:tmp.find('\n')]
            self.executabkp(dir_target, self.TSMSCHEDLOG, self.TSMERRORLOG)
        return None

    def executabkp(self, target, file_out, file_err):
        """
        Execute TSM backup of target path
        :param target: path to backup
        :param file_out: File that receives the output of command
        :param file_err: File that receives the errors of command
        """
        param_sub = ""
        param_target = ""
        try:
            # separa param '-sub=yes' do caminho alvo
            param_sub, param_target = target.split(' ', 1)
        except ValueError:
            print("Error: not enough values to unpack")
            print(target)
            exit(-1)
        cmd = [self.DSMC, "i",  "-quiet", "-se=" + self.NODENAME, param_sub, param_target]
        print(cmd)
        secs = 1
        while self.PID_CONTROL.__len__().__gt__(30):
            time.sleep(secs)
            secs *= 2
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.PID_CONTROL.append(proc.pid)
        outs = ""
        errs = ""
        try:
            outs, errs = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        finally:
            self.writeonfilebytes(file_out, outs)
            self.writeonfilebytes(file_err, errs)
            proc.wait()
            """
            proc_count = 0
            while proc.poll() is None:
                # flag_done = proc.poll().__ne__(None)    # if proc hasn't terminet yet, it returns None.
                # flag_done is true if
                proc_count += 1
                print("proc {0} is running. \'While\' ran {1} times.\n ".format(proc.pid, proc_count))
                """
            if proc.poll() is not None:
                print("PID {0} done.".format(proc.pid))
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
        tmp_file = tempfile.TemporaryFile(mode="w+")
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


def main():
    """
    Main
    :return:
    """
    bkp = BkpNasSeg()
    if not bkp.testlevel:
        print("Programa terminado.")
        exit(-1)
    bkp.generatetextfile()
    linhas = bkp.file_len(bkp.FILENODE)
    print(linhas)
    threads = 0
    # enquanto tiver arquivos a serem copiados
    flag_execute = True
    while flag_execute:
        # ate 10 threads
        if bkp.PID_CONTROL.__len__().__lt__(10):
            try:
                _thread.start_new_thread(bkp.dsmcdecrementa, ())
                threads += 1
            except RuntimeError:
                print("Error: unable to start thread")
            finally:
                linhas = bkp.file_len(bkp.FILENODE)
                print("thread " + str(threads))
                print(linhas)
                time.sleep(0.1)
                for pid in bkp.PID_CONTROL:
                    print(str(pid))
                print("Total ative processes: " + str(bkp.PID_CONTROL.__len__()))
        flag_execute = bkp.PID_CONTROL.__len__().__gt__(0)
    return 0


if __name__ == "__main__":
    main()
