import string
from collections import OrderedDict
from os import chdir, mkdir
from os.path import join


class GenerateDsmSysConfig:
    CONFIG_DICT = None

    def __init__(self, nodename, base_dir):
        self.NODENAME = nodename
        self.NODESBASEDIR = "NODES"             # path where all node dirs are placed -- Will be changed to 'NODES'
        self.BINDIR = '/usr/tivoli/tsm/client/ba/bin64'
        self.NODE_FULL_DIR = join(self.BINDIR, self.NODESBASEDIR, self.NODENAME)
        self.LOGDIR = join(self.NODE_FULL_DIR, 'logs')
        self.MAIL_DIR = 'cyrus/mail'
        self.BASE_DIR = base_dir                   # path to be copied
        self.BKP_NAS_SEG_PATH = '/opt/tsm_seg_bkp_python/tsm_seg_bkp/bkp_nas_seg.py'
        self.MAIL_FULL_DIR = join(self.BASE_DIR, self.MAIL_DIR)
        self.CONFIG_DICT = OrderedDict([('SERVERNAME', nodename),
                                        ('NodeName', nodename),
                                        ('CommMethod', 'tcpip'),
                                        ('TcpPort', '1500'),
                                        ('PasswordAccess', 'generate'),
                                        ('tcpbuffsize', '512'),
                                        ('txnbytelimit', '102400'),
                                        ('tcpnodelay', 'yes'),
                                        ('passworddir', self.BINDIR),
                                        ('ERRORLOGNAME', join(self.LOGDIR, 'dsmerror-{0}.log'.format(nodename))),
                                        ('SCHEDLOGNAME', join(self.LOGDIR, 'dsmsched-{0}.log'.format(nodename))),
                                        ('ChangingRetries', '0'),
                                        ('CommRestartD', '120'),
                                        ('CommRestartI', '300'),
                                        ('Schedmode', 'PRompted'),
                                        ('resourceutilization', '10')])

    @staticmethod
    def header_generator(_nodename):
        header = ''
        for i in range(5):
            header += '*'
            if i == 0 or i == 4:
                header += '*' * 58
            if i == 1 or i == 3:
                header += ' '*58
            if i == 2:
                h_space = ((58 - _nodename.__len__()) / 2).__int__()
                header += ' '*h_space
                header += _nodename
                header += ' '*(58 - h_space - _nodename.__len__())
            header += '*\n'
        return header

    @staticmethod
    def generate_session_footer():
        footer = '*' * 60 + '\n'
        return footer

    def connection_config(self, letter):
        pass

    def get_dict(self):
        return self.CONFIG_DICT

    def strigfy_dict(self, config_dict):
        result = ''
        for keyword in config_dict:
            result += keyword + self.space_tab(keyword) + config_dict[keyword] + '\n'
        return result

    def get_filespaces(self, variable='1'):
        """
        Returns filespaces
        :param variable:
        :return:
        """
        cmd = 'dsmc q files -optfile='
        opt_name = 'dsm-' + self.NODENAME + '-' + variable+'.opt'
        opt_path = join(self.BINDIR, self.NODESBASEDIR, self.NODENAME)
        grep_filter = '|grep cyrus'
        awk_filter = '|awk \'{print $5}\''
        from os import popen
        fs_list = popen(cmd+opt_name+opt_path+grep_filter+awk_filter).read().splitlines()
        return fs_list

    def generate_servername(self, letter):
        return self.NODENAME + '-' + letter.upper()

    def generate_letter_path(self, letter):
        lp = join(self.MAIL_FULL_DIR, letter)
        return lp

    def generate_incexcl(self, letter):
        import string
        retention = 'EXPRESSO_30D'
        inclexcl = 'DIRMC   ' + retention + '\n'
        inclexcl += 'EXCLUDE /*\n'
        inclexcl += 'EXCLUDE /.../*\n'
        inclexcl_line = 'INCLUDE \"' + self.generate_letter_path(letter) + '*' + '/.../*' + '\"'
        inclexcl_line += ' '*((80 - retention.__len__()) - inclexcl_line.__len__()) + retention + '\n'
        inclexcl += inclexcl_line
        excl_letters = string.ascii_lowercase.replace(letter, '')
        inclexcl += 'EXCLUDE.DIR "/[' + excl_letters + ']*"\n'
        inclexcl += 'EXCLUDE.DIR /.../.snapshot\n'
        return inclexcl

    def generate_domain(self, letter):
        do = 'Domain '
        do += self.generate_letter_path(letter) + '\n'
        return do

    def generate_virtualmountpoint(self, letter):
        vm = 'Virtualmountpoint '
        vm += self.generate_letter_path(letter) + '\n'
        return vm

    def generate_letter_config_name(self, letter):
        name = "config_"
        name += self.NODENAME
        name += "-" + letter.upper() + ".json"
        return name

    def generate_letter_config(self, letter):
        servername = self.generate_servername(letter)
        self.CONFIG_DICT['SERVERNAME'] = servername
        lc = self.strigfy_dict(self.CONFIG_DICT)
        lc += self.generate_domain(letter)
        lc += self.generate_virtualmountpoint(letter)
        lc += self.generate_incexcl(letter)
        lc += self.generate_session_footer()
        return lc

    def generate_all_configs(self):
        """Creates dsm.sys content about this node"""
        ac = ''
        for letter in string.ascii_lowercase:
            ac += self.generate_letter_config(letter)
            if letter == 's':
                ac += self.generate_letter_config('stage.')
        ac += self.generate_session_footer()*3
        return ac

    @staticmethod
    def space_tab(key_string):
        return ' '*(22 - key_string.__len__())

    def generate_opt_file_content(self, letter):
        keys = ['servername', 'skipaclupdate', 'skipacl']
        content = ''
        for key in keys:
            if key == 'servername':
                content = key.upper() + self.space_tab(keys[0]) + self.generate_servername(letter)
            else:
                content += key.upper() + self.space_tab(keys[1]) + 'yes'
        return content

    def generate_opt_filename(self, letter):
        """TODO"""
        name = 'dsm-' + self.NODENAME + '-' + letter.upper() + '.opt'
        return name

    def create_all_opt(self):
        s = str(string.ascii_lowercase)
        for letter in s:
            file_name = self.generate_opt_filename(letter)
            file_name = join(self.NODE_FULL_DIR, file_name)
            content = self.generate_opt_file_content(letter)
            self.save_file(content, file_name)
        return None

    def generate_python_script(self):
        content = "#!/bin/sh\n"
        content += "DTHR=\"`date +%y%m%d.%H%M%S`\"\n\n"
        s = str(string.ascii_lowercase)
        s = 'z' + s[:-1]
        for letter in s:
            content += "python3 " + join(self.NODE_FULL_DIR, self.generate_letter_config_name(letter))
            content += " > bkp_nas_seg.$DTHR.log\n"
            if letter == 's':
                content += "python3 " + join(self.NODE_FULL_DIR, self.generate_letter_config_name('stage.'))
                content += " > bkp_nas_seg.$DTHR.log\n"
        return content

    def save_file(self, content, file_name):
        with open(file_name, mode="w") as fl:
            fl.write(content)
        return file_name

    def generate_adsm_script(self):
        """TODO"""
        optfile = join(self.NODE_FULL_DIR, self.generate_opt_filename('A'))
        content = '''
#
# Start ADSM scheduler
#

SERVER="{nodename}"
LOGDIR="/restore/DIOPE/expresso/logs"
status1=`ps -ef | grep $SERVER | grep -v grep`

if [ "$status1" = "" ]
then
    if [ ! -d $LOGDIR ]
    then
        mkdir $LOGDIR
    fi
    cd $LOGDIR

    > dsmsched.pru
    > dsmerlog.pru
#    nohup dsmcad -optfile={optfile} > /dev/null 2>&1 &
     nohup dsmc sched -se=$SERVER -optfile={optfile} > /dev/null 2>&1 &
fi

exit 0
'''.format(nodename=self.NODENAME.upper(), optfile=optfile)
        return content

    def create_node_dir(self):
        try:
            mkdir(self.NODE_FULL_DIR)
            return True
        except Exception as e:
            print(e.__str__())
            return False

    def generate_json_content(self, letter):
        content = '{\n' 
        content += '"PROCS": 30,\n'
        content += '"LEVEL_THRESHOLD": 2,\n'
        content += '"LEVEL_MAXLIMIT": 2,\n'
        content += '"BASE_DIR": ["{0}"],\n'.format(self.generate_letter_path(letter))
        content += '"NODENAME": "{0}",\n'.format(self.NODENAME)
        content += '"OPTFILE": "{0}",\n'.format(join(self.NODE_FULL_DIR, self.generate_opt_filename(letter)))
        content += '"TSM_DIR": "{0}",\n'.format(self.BINDIR)
        content += '"TSM_LOG_DIR": "{0}",\n'.format(self.LOGDIR)
        content += '"TMP_DIR": "{0}",\n'.format('/tmp/tsm_seg_bkp/')
        content += '"DSMC": "{0}",\n'.format('/usr/bin/dsmc')
        content += '"VERBOSE": False\n'
        content += '}'
        return content

    def generate_json_name(self, letter):
        file_name = 'config_' + self.NODENAME
        file_name += '-' + letter + '.json'
        return file_name

    def create_all_json(self):
        s = str(string.ascii_lowercase)
        for letter in s:
            file_name = self.generate_json_name(letter)
            file_name = join(self.NODE_FULL_DIR, file_name)
            content = self.generate_json_content(letter)
            self.save_file(content, file_name)
        return 0

    def generate_presch_content(self):
        content = '#!/bin/bash\n'
        content += 'NODENAME="{0}"\n'.format(self.NODENAME)
        content += 'LOGDIR="{0}"\n'.format(self.LOGDIR)
        content += 'OPTFILE="{0}"\n\n'.format(join(self.NODE_FULL_DIR, self.generate_opt_filename('a')))
        content += 'dsmc ar -se=$NODENAME -filesonly -optfile=$OPTFILE '  # do not put '\n'
        content += '"$LOGDIR/dsm*$NODENAME*.log.*.gz" -del -archm=LOG-TSM-2M\n'
        content += '> $LOGDIR/nohup.out\n'
        content += '#> $LOGDIR/dsmsched.pru\n'
        content += '#> $LOGDIR/dsmerror.log.pru\n\n'
        content += 'exit 0'
        return content

    def generate_presch_filename(self):
        filename = 'presch-' + self.NODENAME + '.sh'
        return filename

    def generate_postsch_content(self):
        content = 'NODENAME="{0}"\n'.format(self.NODENAME)
        logerr = 'dsmerror-' + self.NODENAME + '.log'
        logsch = 'dsmsched-' + self.NODENAME + '.log'
        content += 'LOGERR="{0}"\n'.format(join(self.LOGDIR, logerr))
        content += 'LOGERR="{0}"\n'.format(join(self.LOGDIR, logsch))
        content += 'E_MAIL="lista-diope-tsm.forward@celepar.pr.gov.br"\n\n'
        content += 'if [ -s $LOGERR ] then\n'
        content += ' '*4 + 'cat $LOGERR | mail -s "Verificar TSM `hostname`-$NODENAME" -v $E_MAIL\n'
        content += 'fi\n'
        content += 'DTHR="`date +%y%m%d.%H%M%S`"\n'
        content += 'cp $LOGERR $LOGERR.$DTHR && gzip $LOGERR.$DTHR && > $LOGERR\n'
        content += 'cp $LOGSCH $LOGSCH.$DTHR && gzip $LOGSCH.$DTHR && > $LOGSCH\n'
        content += 'exit 0'
        return content

    def generate_postsch_filename(self):
        filename = 'postch-' + self.NODENAME + '.sh'
        return filename

    def deploy_dsm_sys(self, filename):
        content = '#!/bin/bash\n'
        content += 'ORIGIN_FILE = "{0}"\n'.format(filename)
        content += 'TARGET_FILE = "{0}"\n\n'.format(join(self.BINDIR, 'dsm.sys'))
        content += 'cat $ORIGIN_FILE >> $TARGET_FILE\n'
        content += '\n'
        return content

    def main(self):
        if self.create_node_dir():
            # create node dir
            chdir(self.NODE_FULL_DIR)
            # create logdir
            mkdir(self.LOGDIR)
            # create adsm
            content = self.generate_adsm_script()
            file_name = 'adsm-' + self.NODENAME + '.sh'
            self.save_file(content, join(self.NODE_FULL_DIR, file_name))
            # create optfile
            self.create_all_opt()
            # create sysfile
            content = self.generate_all_configs()
            file_name = 'dsm-' + self.NODENAME + '.sys.local'
            self.save_file(content, join(self.NODE_FULL_DIR, file_name))
            # create script to deploy sysfile

            # create pre
            content = self.generate_presch_content()
            file_name = self.generate_presch_filename()
            self.save_file(content, file_name)
            # create pos
            content = self.generate_postsch_content()
            file_name = self.generate_postsch_filename()
            self.save_file(content, file_name)
            # create python_script
            content = self.generate_python_script()
            file_name = self.generate_
            self.save_file(content, file_name)
            # create json
            self.create_all_json()
        else:
            print('This program cannot continue.')
            exit(1)
        exit(0)


if __name__ == '__main__':
    import sys
    nodename = sys.argv[1]
    basedir = sys.argv[2]
    d = GenerateDsmSysConfig(nodename, basedir)
    d.main()