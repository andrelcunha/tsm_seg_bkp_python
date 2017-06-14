#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Executes a segmented backup from target path, setup in BASE_DIR attribute.
"""

import os
import _thread
import time
import tempfile
import errno
import subprocess
import json


class BkpNasSeg:
    """
    Executes a segmented backup from target path, setup in BASE_DIR attribute.
    """
    PROCS = 0
    LEVELS = 0
    LEVEL_THRESHOULD = 0
    BASE_DIR = ""
    NODENAME = ""
    TSM_DIR = "/opt/tivoli/tsm/client/ba/bin"
    TMP_DIR = "/tmp/tsm_seg_bkp/"
    DSMC = "/usr/bin/dsmc"
    TXT_DIR = TSM_DIR + "/TXT"
    NOMEDIR = BASE_DIR.replace("/", "")
    FILENODE = TXT_DIR + "/" + NODENAME + "-" + NOMEDIR + ".txt"
    DATE = time.strftime("%d%m%y-%H%M%S")
    TSMSCHEDLOG = TSM_DIR + "/logs/dsmsched-" + NODENAME + ".log"
    TSMERRORLOG = TSM_DIR + "/logs/dsmerror-" + NODENAME + ".log"
    PID_CONTROL = []

    def __init__(self):
        self.make_sure_path_exists(self.TXT_DIR)
        self.make_sure_file_exists(self.FILENODE)
        print(self.FILENODE)

    @staticmethod
    def get_configuration():
        """
        Get configuration from config file
        :return: json
        """
        with open('strings.json') as json_data:
            config = json.load(json_data)
        return config[0]

    def set_configuration(self,config):
        for attrib in dir(self):
            if config.__contains__(attrib):
                setattr(self, attrib, json[attrib])

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
            if level == self.LEVELS:
                file_level = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-NIVEL" + str(level) + ".txt"
                aux = "*/"
                cmd = "ls -1 -d " + self.BASE_DIR + "/"
                cmd += level * aux
                cmd += " > " + file_level
                os.system(cmd)
                # cmd content reset after execution
                cmd = "sed 's/^/-sub=yes \"/' " + file_level + " >> " + self.FILENODE
                os.system(cmd)
                cmd = "rm -f " + file_level
                os.system(cmd)
            elif self.LEVELS > level:
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

    '''
       #Função dsmcdecrementa - Executa backups incrementais em paralelo, para as primeiras $PROCS linhas do arquivo de
        diretórios. 
       #Depois exclui estas linhas da lista de diretórios, e decrementa a várial de contabilização do número de linhas 
       ($LINHAS).


       `sed "$PROCS"q $TXT_DIR/$NODENAME-$NOMEDIR.txt > $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt`
           while [ `cat $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt | wc -l` -gt 0 ]
               do
               DIR=`sed 1q $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt`
               $DSMC i -se=$NODENAME $DIR 1>> $TSM_DIR/logs/dsmsched-$NODENAME.log 2>> $TSM_DIR/logs/dsmerror-$NODENAME.
               log
               `sed 1d $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt > $TXT_DIR/$NODENAME-$NOMEDIR-CICLO-TEMP.txt`
               `mv $TXT_DIR/$NODENAME-$NOMEDIR-CICLO-TEMP.txt $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt`
               done
       `sed "1,"$PROCS"d" $TXT_DIR/$NODENAME-$NOMEDIR.txt > $TXT_DIR/$NODENAME-$NOMEDIR-DECREM.txt`
       `mv $TXT_DIR/$NODENAME-$NOMEDIR-DECREM.txt $TXT_DIR/$NODENAME-$NOMEDIR.txt`

       '''

    def dsmcdecrementa(self):
        """
        Executa backups incrementais em paralelo, para as primeiras $PROCS linhas do arquivo de diretórios.
        Depois exclui estas linhas da lista de diretórios, e decrementa a várial de contabilização do número de linhas
        ($LINHAS).
        """
        file_node_ciclo = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-CICLO"
        file_node_ciclo += ".txt"
        self.writeonfile(file_node_ciclo, self.pop_out_n_lines(self.FILENODE, self.PROCS));
        while self.file_len(file_node_ciclo) > 0:
            dir_target = self.pop_out_n_lines(file_node_ciclo, 1).rstrip('\n')
            self.executabkp(dir_target, self.TSMSCHEDLOG, self.TSMERRORLOG)
        return None

    def executabkp(self, target, file_out, file_err):
        """
        Execute TSM backup of target path
        :param target: path to backup
        :param file_out: File that receives the output of command
        :param file_err: File that receives the errors of command
        """
        param_sub, param_target = target.split(' ', 1)
        cmd = [self.DSMC, "i",  "-quiet", "-se=" + self.NODENAME, param_sub, param_target]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.PID_CONTROL.append(proc.pid)
        try:
            outs, errs = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        finally:
            self.writeonfilebytes(file_out, outs)
            self.writeonfilebytes(file_err, errs)
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

'''
    def pid_control(self):
        for pid in self.PID_CONTROL:
            proc = new subprocess.
            # if 
'''

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
    # Fazer thread para controlar os pids.
    while linhas > 0:
        try:
            _thread.start_new_thread(bkp.dsmcdecrementa, ())
        except RuntimeError:
            print("Error: unable to start thread")
        finally:
            linhas = bkp.file_len(bkp.FILENODE)
            time.sleep(10)
    return None


def testa_setup():
    bkp = BkpNasSeg()
    my_json = bkp.get_configuration()
    bkp.set_configuration(my_json)
    print(bkp.TSM_DIR)

if __name__ == "__main__":
    # main()
    testa_setup()

