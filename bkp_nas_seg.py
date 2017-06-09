#!/usr/bin/python3

import os
import _thread
import time

class bkpNasSeg:
    def __int__(self):
        self.PROCS=30
        self.LEVELS=3
        self.LEVEL_THRESHOULD=5
        self.BASE_DIR="/clientes/SEED"
        self.NODENAME="BA-NAS-SEED"
        self.NOMEDIR = self.BASE_DIR.replace("/","")
        self.FILENODE = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + ".txt"
        self.TSM_DIR="/usr/tivoli/tsm/client/ba/bin64"
        self.TXT_DIR=self.TSM_DIR+"/TXT"
        self.DSMC="/usr/bin/dsmc"
        self.DATE=time.strftime("%d%m%y-%H%M%S")
        self.TSMSCHEDLOG = self.TSM_DIR+"/logs/dsmsched-"+self.NODENAME+".log"
        self.TSMERRORLOG = self.TSM_DIR + "/logs/dsmerror-" + self.NODENAME + ".log"
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

    def writeOnFile(self,file_name,message):
        my_file = open( file_name, mode="r+" )
        my_file.write( message )
        my_file.close()
        return None

    def testLevel(self):
        msg = "Níveis de segmentação devem estar entre um (1) e cinco (5)"
        flag_ok=True
        if self.LEVELS <1 or self.LEVELS > 5:
            self.writeOnFile(self.TSMSCHEDLOG, msg)
            self.writeOnFile(self.TSMERRORLOG, msg)
            flag_ok=False
        return flag_ok

    def generateTextFile(self):
        ''' Geração do arquivo texto com todos os diretórios que sofrerão backup,
        incluíndo a opção de sub=yes ou sub=no em cada linha.'''
        for level in range(1,5):
            if level == self.LEVELS:
                file_level=self.TXT_DIR+ "/" + self.NODENAME+"-"+self.NOMEDIR+"-NIVEL"+str(level)+".txt"
                aux= "*/"
                cmd= "ls -1 -d "+self.BASE_DIR+"/"
                cmd+= level*aux
                cmd+= " > "+ file_level
                os.system(cmd)
                #cmd content reset after execution
                cmd="sed 's/^/-sub=yes \"/' "+ file_level +" >> "+ self.FILENODE
                os.system(cmd)
                cmd="rm -f "+file_level
                os.system(cmd)
            elif self.LEVELS > level:
                file_level = self.TXT_DIR + "/" + self.NODENAME + "-" + self.NOMEDIR + "-NIVEL" + str(level) + ".txt"
                aux = "*/"
                cmd = "ls -1 -d " + self.BASE_DIR + "/"
                cmd += level * aux
                cmd += " > " + file_level
                os.system(cmd)
                # cmd content reset after execution
                cmd = "sed 's/^/-sub=no \"/' " + file_level + " >> " + file_node
                os.system(cmd)
                cmd = "rm -f " + file_level
                os.system(cmd)
        file_list= self.TXT_DIR+"/"+self.NODENAME+"-"+self.NOMEDIR + "-LISTADIR.txt"
        cmd = "sed \"/.snapshot/d\"" + self.FILENODE + "> " + file_list
        os.system(cmd)
        cmd = "sed 's/$/\"/' " + file_list + ">" + self.FILENODE
        os.system(cmd)
        cmd = "rm -f " + file_list
        return None

    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def dsmcDecrementa(self, threadName):
        count = 0
        while count < 5:
            time.sleep(10)
            count += 1
            print("%s: %s", threadName, time.ctime(time.time()))
        return None

    def main(self):
        if not(self.testLevel()):
            print("Programa terminado.")
            return -1
        self.generateTextFile()
        linhas = self.file_len(self.FILENODE)
        while linhas >0:
            try:
                _thread.start_new_thread( self.dsmcDecrementa,("thread"+str(time.time())))
            except:
                print ("Error: unable to start thread")
        return None

if __name__=="__main__":
    bkp = bkpNasSeg
    bkp.main()