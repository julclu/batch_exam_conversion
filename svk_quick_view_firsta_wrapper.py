#!/usr/bin/env python

import os
import glob
import argparse 
import subprocess as sub
import shlex 
from subprocess import PIPE, Popen
import pandas as pd
import logging
import re

print('creating argument parser')
########### Create an argument parser 
parser = argparse.ArgumentParser(description='Label tool for firsta image.')
parser.add_argument('bnum', type=str, nargs=1, help='Input the b-number of the patient.')
parser.add_argument('tnum', metavar = 't', type =str, nargs = 1, help = 'Input the t-number of the scan.')
print('parsing the arg')
args = parser.parse_args()
bnum = ''.join(args.bnum)
tnum = ''.join(args.tnum)

print('changing path')
def change_path(pathname_root):
    pathname = pathname_root+bnum+'/'+tnum
    os.chdir(pathname)
change_path(recgli_path_root)

if len(glob.glob('*/*firsta.idf'))>1: 
	first_path = glob.glob('*/*firsta.idf')[0]
else: 
	first_path = glob.glob('*/*first.idf')[0]

svk_quick_view_command = 'svk_quick_view '+first_path
try:
	print('Look through perfusion to see if fully blood:')
	sub.call(svk_quick_view_command, shell = True)
	valid_perf = input('Is the perfusion image valid? y/m/n: ')
	if valid_perf == "y" or valid_perf == "n" or valid_perf == "m": 
		perf_valid_file = open('perf_valid_file.csv',"w+") 
		perf_valid_file.write(bnum+","+tnum+","+valid_perf)
		perf_valid_file.close()
	else: 
		print('error: please input y for yes, n for no, or m for maybe.')
		valid_perf = input('Is the perfusion image valid? y/m/n: ')
except Exception as error:
	print('there was an error loading this image')
	perf_valid_file = open('perf_valid_file.csv', "w+")
	perf_valid_file.write(bnum+","+tnum+","+valid_perf)
	perf_valid_file.close()
