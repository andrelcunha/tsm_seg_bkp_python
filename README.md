# tsm_seg_bkp_python

Python application to backup files from one node in segmented mode, through Tivoli Storage Manager (TSM).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

It is necessary that it has python 3 installed on the machine.
There is no other package as prerequisite besides nosetest. You can get it running this command:
```
pip3 install -r requirements.txt
```

### Installing

Just copy the inner folder tsm_seg_bkp in a place of your choice.

## Using

As you can see, there is three files in tsm_seg_bkp (actually, there is four, but __int__.py, it doesn't count) :
* bkp_nas_seg.py \- main file. This file is responsable for execute backup of the given path.
* level_listdir.py \- Lists the directories in the designated path. It can be used in standalone mode, but is necessary for the proper execution of bkp_nas_seg
* path_generator.py \- It is a standalone utility, used to test a non-production path.

To use bkp_nas_seg, you will need a json config file. If you run it without parameters, it will generate a file called config.json.
The structure of this config file is:
```
{
"PROCS": 30,
"LEVEL_THRESHOLD": 3,
"LEVEL_MAXLIMIT": 5,
"BASE_DIR": "/home",
"NODENAME": "_MYNODE_",
"OPTFILE": "/opt/tivoli/tsm/client/ba/bin/dsm.opt",
"TSM_DIR": "/opt/tivoli/tsm/client/ba/bin",
"TMP_DIR": "/tmp/tsm_seg_bkp/",
"DSMC": "/usr/bin/dsmc"
}
```
 * PROCS - this parameter sets the quantity of processes managed by each thread.
 * LEVEL_THRESHOLD - it is the level when the tsm stops copying folder by folder with the parameter subdir=no, and pass to copy all the subdirectories beneath the current path.
 * LEVEL_MAXLIMIT - the maximum deep that the program level_dir must dive. It is noteworthy that the LEVEL_THRESHOLD must be lesser than LEVEL_MAXLIMIT, otherwise the program will crash.
 * BASE_DIR - the path that tsm will copy, with all its content.
 * NODENAME - the name of the node configured in tsm.
 * OPTFILE - the options file for that node.
 * TSM_DIR - path of the tsm client
 * TMP_DIR - the tmp directory where the program will create temporary files.
 * DSMC - path to the tsm binary file.

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Andre Luis da Cunha** - *Initial work* - [andrelcunha](https://github.com/andrelcunha)

See also the list of [contributors](https://github.com/andrelcunha/tsm_seg_bkp_python/contributors) who participated in this project.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

*    Thanks to PurpleBooth for the CONTRIBUTING.md.
*    Thanks to kennethreitz for Python project guidelines. In the future, I will contribute with the community helping to translate his book to Brazilian Portuguese. I hope I have enought time for this :wink:
