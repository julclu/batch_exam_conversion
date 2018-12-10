#!/usr/bin/env python

import os
import glob
import argparse 
import subprocess as sub
import shlex 
from subprocess import PIPE, Popen
import pandas as pd

print('creating argument parser')
########### Create an argument parser 
parser = argparse.ArgumentParser(description='In this script we will import a single bnum/tnum, run the archive_exam perl script, and then dcm_qr to desired location.')
parser.add_argument('bnum', type=str, nargs=1, help='Input the b-number of the patient.')
parser.add_argument('tnum', metavar = 't', type =str, nargs = 1, help = 'Input the t-number of the scan.')
parser.add_argument('--config_file_path', metavar = "C", default = '/data/RECglioma/archived/convert_exam_original.cfg', type = str, nargs = 1, help = 'input the path to the config file')
print('parsing the arg')
args = parser.parse_args()
bnum = ''.join(args.bnum)
tnum = ''.join(args.tnum)
config_file_path = "".join(args.config_file_path)


preop_path_root = "/data/bioe4/po1_preop_recur/"
recgli_path_root = '/data/RECglioma/archived/'

def change_path(pathname_root):
    pathname = pathname_root+bnum+'/'+tnum
    os.chdir(pathname)

change_path(preop_path_root)
sfnum = glob.glob("sf*")
numeric_sfnum = sfnum[0][2:]
change_path(recgli_path_root)
copy_command = "cp "+sfnum[0]+" ."
dirs_in_tnum_already = os.listdir()
if 'roi_analysis' not in dirs_in_tnum_already: 
	os.mkdir('roi_analysis')
	os.chdir('roi_analysis')
	biopsy_make_masks_command = 'biopsy_make_masks --sf '+numeric_sfnum+" -i ../images/"+tnum+"_t1ca -d 5"
	sub.call(biopsy_make_masks_command, shell = True)
else:
	print('roi_analysis folder exists, moving on.')