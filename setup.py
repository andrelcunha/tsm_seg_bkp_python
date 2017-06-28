# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='tsm_seg_bkp_python',
    version='0.2.1',
    description='Tool to backup a path using TSM, in a segmented way.',
    long_description=readme,
    author='Andre Luis da Cunha',
    author_email='andre.l.cunha@live.com',
    url='https://github.com/andrelcunha/tsm_seg_bkp_python',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
