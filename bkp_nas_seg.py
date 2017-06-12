#!/usr/bin/python3

import os
import _thread
import time
import tempfile


class BkpNasSeg:
    PROCS = 30
    LEVELS = 3
    LEVEL_THRESHOULD = 5
#    BASE_DIR = "/clientes/SEED"
    BASE_DIR = "/Users/deko"
    NODENAME = "BA-NAS-SEED"
    NOMEDIR = BASE_DIR.replace("/", "")
#    TSM_DIR = "/usr/tivoli/tsm/client/ba/bin64"
    TSM_DIR = "/tmp/TSM"
    TXT_DIR = TSM_DIR + "/TXT"
    FILENODE = TXT_DIR + "/" + NODENAME + "-" + NOMEDIR + ".txt"
    TMP_DIR = "/tmp/tsm_seg_bkp/"
    DSMC = "/usr/bin/dsmc"
    DATE = time.strftime("%d%m%y-%H%M%S")
    TSMSCHEDLOG = TSM_DIR + "/logs/dsmsched-" + NODENAME + ".log"
    TSMERRORLOG = TSM_DIR + "/logs/dsmerror-" + NODENAME + ".log"
    
    def __int__(self):
        if os.path.isfile(self.FILENODE):
            self.createfile(self.FILENODE)
        return None

    @staticmethod
    def createfile(file_name):
        fn = open(file_name, mode="a+")
        fn.close()
        return None

    @staticmethod
    def writeonfile(file_name, message):
        my_file = open(file_name, mode="w")
        my_file.write(message)
        my_file.close()
        return None

    def testlevel(self):
        """Test level configuration"""
        msg = "Níveis de segmentação devem estar entre um (1) e cinco (5)"
        flag_ok = True
        if self.LEVELS < 1 or self.LEVELS > self.LEVEL_THRESHOULD:
            self.writeonfile(self.TSMSCHEDLOG, msg)
            self.writeonfile(self.TSMERRORLOG, msg)
            flag_ok = False
        return flag_ok

    def generatetextfile(self):

        # Geração do arquivo texto com todos os diretórios que sofrerão backup,
        # incluíndo a opção de sub=yes ou sub=no em cada linha.

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
        size = os.stat(fname).st_size
        if size > 0:
            with open(fname) as f:
                for i, l in enumerate(f):
                    pass
            return i + 1
        else:
            return 0

    def dsmcdecrementa_fake(self, threadname):
        count = 0
        file0 = self.FILENODE
        file1 = self.FILENODE+".tmp"
        while count < 5:
            time.sleep(10)
            count += 1
            tmp = self.pop_out_first_lines(file0, file1, 1)
            cmd = "mv " + file1 + " " + file0
            os.system(cmd)
            print("{0} - {1}: {2}".format(threadname, count, tmp))
        return None

    '''
       #Função dsmcdecrementa - Executa backups incrementais em paralelo, para as primeiras $PROCS linhas do arquivo de diretórios. 
       #Depois exclui estas linhas da lista de diretórios, e decrementa a várial de contabilização do número de linhas ($LINHAS).


       `sed "$PROCS"q $TXT_DIR/$NODENAME-$NOMEDIR.txt > $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt`
           while [ `cat $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt | wc -l` -gt 0 ]
               do
               DIR=`sed 1q $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt`
               $DSMC i -se=$NODENAME $DIR 1>> $TSM_DIR/logs/dsmsched-$NODENAME.log 2>> $TSM_DIR/logs/dsmerror-$NODENAME.log
               `sed 1d $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt > $TXT_DIR/$NODENAME-$NOMEDIR-CICLO-TEMP.txt`
               `mv $TXT_DIR/$NODENAME-$NOMEDIR-CICLO-TEMP.txt $TXT_DIR/$NODENAME-$NOMEDIR-CICLO.txt`
               done
       `sed "1,"$PROCS"d" $TXT_DIR/$NODENAME-$NOMEDIR.txt > $TXT_DIR/$NODENAME-$NOMEDIR-DECREM.txt`
       `mv $TXT_DIR/$NODENAME-$NOMEDIR-DECREM.txt $TXT_DIR/$NODENAME-$NOMEDIR.txt`

       '''

    def dsmcdecrementa(self):
        cmd = ""
        file_node_ciclo = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-CICLO"
        file_node_ciclo_tmp = file_node_ciclo
        file_node_ciclo += ".txt"
        file_node_ciclo_tmp += ".txt"
        cmd += "sed " + str(self.PROCS) + "q " + self.FILENODE + " > " + file_node_ciclo
        os.system(cmd)
        while self.file_len(file_node_ciclo) > 0:
            # dir_target = self.pop_out_first_lines(file_node_ciclo, file_node_ciclo_tmp, 1)
            dir_target = self.pop_out_first_lines(file_node_ciclo, 1)
            self.executabkp(dir_target)
        return None

    def executabkp(self, target):
        cmd = self.DSMC + " i -se=" + self.NODENAME + target
        cmd += " 1>> " + self.TSMSCHEDLOG + " 2>> " + self.TSMERRORLOG
        os.system("echo " + cmd)
        return None

    @staticmethod
    def pop_out_first_lines(input_file, lines):
        fst_lines = ""
        tmp_file = tempfile.TemporaryFile(mode="w+")
        inputf = open(input_file, "r")
        for i, line in enumerate(inputf):
            if i < lines:
                fst_lines += line
            else:
                tmp_file.write(line)
        inputf.close()
        tmp_file.seek(0)
        with open(input_file, mode="w") as inputf:
            for line in tmp_file:
                inputf.write(line)
        tmp_file.close()
        # os.system("mv " + output_file + " " + input_file)
        return fst_lines


def main(self):
    if not self.testlevel:
        print("Programa terminado.")
        return -1
    self.generatetextfile(self)
    linhas = self.file_len(self.FILENODE)
    while linhas > 0:
        try:
            _thread.start_new_thread(self.dsmcdecrementa, (self, ))
        except RuntimeError:
            print("Error: unable to start thread")
        linhas = self.file_len(self.FILENODE)
        time.sleep(30)
    return None

if __name__ == "__main__":
    bkp = BkpNasSeg
    main(bkp)
