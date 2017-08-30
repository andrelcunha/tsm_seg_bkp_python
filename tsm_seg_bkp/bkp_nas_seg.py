#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
Executes a segmented backup from target path, setup in BASE_DIR attribute.
"""
import json
# import _thread
import multiprocessing
import os
import os.path
import time
from tempfile import TemporaryFile

import tsm_seg_bkp.level_listdir
import tsm_seg_bkp.tools


class BkpNasSeg:
    """
    Executes a segmented backup from target path, setup in BASE_DIR attribute.
    """

    def __init__(self, config_file):
        from tsm_seg_bkp.tools import create_timestamp, make_sure_path_exists, make_sure_file_exists
        self.PROCS = 0
        self.LEVEL_THRESHOLD = 0
        self.LEVEL_MAXLIMIT = 0
        self.BASE_DIR = ""
        self.NODENAME = ""
        self.OPTFILE = ""
        self.TSM_DIR = ""
        self.TSM_LOG_DIR = ""
        self.TMP_DIR = ""
        self.DSMC = ""
        self.TXT_DIR = ""
        # self.NOMEDIR = ""
        self.FILENODE = ""
        self.TSMSCHEDLOG = ""
        self.TSMERRORLOG = ""
        self.PID_CONTROL = []
        self.VERBOSE = False
        self.debug = True
        self.sudo = False
        self.set_configuration(self.get_configuration(config_file))
        self.TIMESTAMP = create_timestamp()
        if self.VERBOSE == "True":
            self.VERBOSE = True
        else:
            self.VERBOSE = False
        # self.NOMEDIR = self.BASE_DIR.replace("/", "")
        self.TXT_DIR = os.path.join(self.TSM_DIR, "TXT")
        self.FILENODE = os.path.join(self.TXT_DIR, self.NODENAME + "-" + self.TIMESTAMP + ".txt")
        self.TSMSCHEDLOG = os.path.join(self.TSM_LOG_DIR, "dsmsched-" + self.NODENAME + ".log")
        self.TSMERRORLOG = os.path.join(self.TSM_LOG_DIR, "dsmerror-" + self.NODENAME + ".log")
        self.PID_CONTROL = []
        make_sure_path_exists(self.TXT_DIR)
        make_sure_file_exists(self.FILENODE)
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
    def testlevel(level_threshold, level_max):
        """
        Test 'level' configuration. Unnecessery by now.
        Testa configuração de 'nivel'
        :param: None
        :return: flag_ok: Boolean"""
        return (0 < level_max < 6) and (level_threshold <= level_max) and (level_threshold > 0)

    def generatetextfile(self, base_dir, level_maxlimit=1):
        """
        TODO:
        think about toggle
        file_level = file_level_list[level - 1]
        by
        file_level = file_level_list[level - 1]
        Generate text file with all directories that will be backed up,
        including sub=yes or sub=no option on each line.

        Geração do arquivo texto com todos os diretórios que sofrerão backup,
        incluíndo a opção de sub=yes ou sub=no em cada linha.
        :param: None
        :return None
        """
        file_level_list = []
        lld_list = []
        if type(base_dir) is str:
            base_dir = [base_dir]
        for i,bdir in enumerate(base_dir):
            lld_list.extend([tsm_seg_bkp.level_listdir.LevelListDir(bdir, level_maxlimit)])
            file_level_list.extend(lld_list[i].get_levellist())
        for level in range(1, level_maxlimit + 1):
            if level.__le__(level_maxlimit):  # it was self.LEVEL_THRESHOLD
                file_level = file_level_list[level - 1]
                if level.__lt__(level_maxlimit):  # it was self.LEVEL_THRESHOLD
                    # cmd = "sed 's/^/-sub=no \"/' " + file_level + " >> " + self.FILENODE
                    cmd = "sed 's/^/-sub=no /' " + file_level + " >> " + self.FILENODE
                    os.system(cmd)
                elif level.__eq__(level_maxlimit):  # it was self.LEVEL_THRESHOLD
                    # cmd = "sed 's/^/-sub=yes \"/' " + file_level + " >> " + self.FILENODE
                    cmd = "sed 's/^/-sub=yes /' " + file_level + " >> " + self.FILENODE
                    os.system(cmd)
        file_list = self.TXT_DIR + "/" + self.NODENAME + "-" + self.TIMESTAMP + "-LISTADIR.txt"
        cmd = "sed \"/.snapshot/d\" " + self.FILENODE + ">> " + file_list
        '''
        this statement can be replaced by str.replace(".snapshot","")
        '''
        os.system(cmd)
        # cmd = "sed 's/$/\/\"/' " + file_list + ">" + self.FILENODE
        cmd = "cat " + file_list + ">" + self.FILENODE
        os.system(cmd)
        cmd = "rm -f " + file_list
        os.system(cmd)
        os.chdir(self.TSM_DIR)
        return None

    '''
    def dsmcdecrementa(self):
        """
        Executa backups incrementais em paralelo, para as primeiras $PROCS linhas do arquivo de diretórios.
        Depois exclui estas linhas da lista de diretórios, decrementando a váriavel de contabilização do número de linhas
        ($LINHAS).
        """
   
        command = self.DSMC
        file_out = self.TSMSCHEDLOG
        file_err = self.TSMERRORLOG
        sudo = self.sudo
        debug = self.debug
        raw_line = self.pop_out_n_lines(self.FILENODE, 1)
        optfile = self.OPTFILE
        dir_target = raw_line.replace('\n', '')
        # dir_target = raw_line.rstrip('\n')
        print(dir_target)
        param_sub, param_target = split_target_str(dir_target, debug)
        cmd = prepare_command(command, param_sub, param_target, optfile, sudo, debug)
        self.execute_command(cmd, file_out, file_err, debug)
        return None
    '''

    def execute_command(self, cmd, file_out, file_err, debug=False):
        """
        Executes TSM backup of the target path.
        :param cmd: list
        :param file_out:
        :param file_err:
        :param debug:
        :return:
        """
        from subprocess import Popen, PIPE
        from tsm_seg_bkp.tools import writeonfilebytes
        
        _proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        self.PID_CONTROL.append(_proc.pid)
        outs, errs = _proc.communicate()
        writeonfilebytes(file_out, outs)
        writeonfilebytes(file_err, errs)
        _proc.wait()
        if _proc.poll() is not None:
            if debug:
                print("PID {PID} done.".format(PID=_proc.pid))
            self.PID_CONTROL.remove(_proc.pid)
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


def prepare_command(raw_cmd, param_sub, param_target, optfile, sudo=False, debug=False, verbose=False):
    """
    Prepare the backup command
    :param command: str base command to be executed i.e: /usr/bin/dsmc
    :param param_sub: str(sub=yes)
    :param param_target: str(path)
    :param optfile: str (path)
    :param sudo: Boolean
    :param debug: Boolean
    :param verbose: Boolean
    :return: str
    """
    cmd = []
    if sudo:
        cmd.extend(["sudo"])
    cmd.extend([raw_cmd])
    cmd.extend(["i"])
    if verbose:
        cmd.extend(["-verbose"])
    else:
        cmd.extend(["-quiet"])
    cmd.extend(["-optfile=" + optfile])
    cmd.extend([param_sub])
    cmd.extend([param_target])
    if debug:
        print(cmd)
    return cmd


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
        if debug:
            print('"target_str:' + target_str + '"')
        param_sub, param_target = target_str.split(' ', 1)
        if debug:
            print('"' + param_target + '"')
    except ValueError as e:
        print("Error: not enough values to unpack")
        print(target_str, e)
        exit(-1)
    return param_sub, param_target


def generate_config_file(config_file):
    """

    :param config_file:
    :return:
    """
    config_content = '{\n' \
                     '"PROCS": 30,\n' \
                     '"LEVEL_THRESHOLD": 3,\n' \
                     '"LEVEL_MAXLIMIT": 5,\n' \
                     '"BASE_DIR": "/home",\n' \
                     '"NODENAME": ["TESTE_CUNHA"],\n' \
                     '"OPTFILE": "/opt/tivoli/tsm/client/ba/bin/dsm.opt",\n' \
                     '"TSM_DIR": "/opt/tivoli/tsm/client/ba/bin",\n' \
                     '"TSM_LOG_DIR": "/opt/tivoli/tsm/client/ba/bin/logs",\n' \
                     '"TMP_DIR": "/tmp/tsm_seg_bkp/",\n' \
                     '"DSMC": "/usr/bin/dsmc",\n' \
                     '"VERBOSE": True\n' \
                     '}'
    with open(config_file, mode="w") as cf:
        cf.write(config_content)

if __name__ == "__main__":
    import sys
    import os.path
    from tsm_seg_bkp.tools import humanize_time, file_len
    try:
        conf_file = ''
        start = time.time()
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
            bkp = BkpNasSeg(conf_file)
            if not bkp.testlevel(bkp.LEVEL_THRESHOLD, bkp.LEVEL_MAXLIMIT):
                msg = "Nível máximo de segmentação devem estar entre um (1) e cinco (5).\n"
                msg += "Valor de corte para ativar backup em subniveis deve não ser maior que o nível máximo.\n"
                msg += "Programa terminado."
                print(msg)
                exit(1)
            start_listing = time.time()
            print("Listing directories started at {start}".format(start=start_listing))
            bkp.generatetextfile(bkp.BASE_DIR, bkp.LEVEL_MAXLIMIT)
            delta = time.time() - start_listing
            print("Elapsed Time while listing directories: {0} days, {1}h {2}m {3}s ".format(*humanize_time(delta)))
            linhas = file_len(bkp.FILENODE)
            print("Initial amount of files to be copied: {linhas}".format(linhas=linhas))
            os.chdir(bkp.TSM_DIR)
            command = bkp.DSMC
            file_out = bkp.TSMSCHEDLOG
            file_err = bkp.TSMERRORLOG
            sudo_flag = bkp.sudo
            debug_flag = bkp.debug
            verbose_flag = bkp.VERBOSE
            optfile = bkp.OPTFILE
            counter = 0
            while linhas > 0:
                if multiprocessing.active_children().__len__().__lt__(bkp.PROCS):
                    try:
                        raw_line = bkp.pop_out_n_lines(bkp.FILENODE, 1)
                        dir_target = raw_line.replace('\n', '/')
                        # dir_target = raw_line.rstrip('\n')
                        if bkp.debug:
                            print(dir_target)
                        param_sub, param_target = split_target_str(dir_target, debug_flag)
                        cmd = prepare_command(command, param_sub, param_target, optfile, sudo_flag, debug_flag, verbose_flag)
                        p = multiprocessing.Process(target=bkp.execute_command, args=(cmd, file_out, file_err))
                        p.start()
                    except RuntimeError:
                        print("Error: unable to start subprocess")
                    finally:
                        linhas = file_len(bkp.FILENODE)
                        if bkp.debug:
                            active_processes = multiprocessing.active_children().__len__()
                            if active_processes:
                                try:
                                    last_process = multiprocessing.active_children()[active_processes-1]
                                    print("Process " + str(last_process.pid))
                                except IndexError as e:
                                    print(e.__str__())
                            print("Lines to be processed: {linhas}".format(linhas=linhas))
                            for pid in bkp.PID_CONTROL:
                                print(str(pid))
                            print("Total ative processes: " + str(active_processes))
                        time.sleep(0.5)
                if counter == 4:
                    counter = 0
                    print("\n")
                    print("Heartbeat")
                    print("\n")
                else:
                    counter += 1
            print("There is no more lines to be processed.")
            while multiprocessing.active_children():
                active_processes = multiprocessing.active_children().__len__()
                print("Processes still working: {0}".format(active_processes))
                time.sleep(60)
            print("Program sucessfully executed.")
        except FileNotFoundError as fnfe:
            print(str(fnfe))
            print("File not found. Please inform a existent path.")
            exit(1)
        print("Elapsed Time: {time}".format(time=(time.time() - start)))
    except KeyboardInterrupt:
        proc_list = multiprocessing.active_children()
        active_processes = proc_list.__len__()
        print("Processes still working: {0}".format(active_processes))
        for proc in proc_list:
            proc.terminate()
        exit(1)


