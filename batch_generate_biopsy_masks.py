#!/usr/bin/env python

import os
import glob
import argparse 
import subprocess as sub
import shlex 
from subprocess import PIPE, Popen
import pandas as pd
import logging

## in this script we want to 
## 0. Create the argument parser
## 1. import all of the bnums and tnums 
## 2. run the archive_exam perl script on it 
## 3. run dcm_qr perl script on it in its new location 



def getting_bnum_tnum_list(bnum_tnum_csv): 
    ########### Get bnum_tnum list: 
    bnum_tnum_csv_root = "/home/sf673542/preop_convert_work/"
    bnum_tnum_df = pd.read_csv(bnum_tnum_csv_root+bnum_tnum_csv, header = None)
    bnum_tnum_df.columns = ['bnum', 'tnum', 'DUMMY']
    return bnum_tnum_df

############# Executing this program 
preop_path_root = "/data/bioe4/po1_preop_recur/"
recgli_path_root = '/data/RECglioma/archived/'
print('creating argument parser')
########### Create an argument parser 
parser = argparse.ArgumentParser(description='In this script we will import a single bnum/tnum, run the archive_exam perl script, and then dcm_qr to desired location.')
parser.add_argument('bnum_tnum_csv', type=str, nargs=1, help='List of bnums in one column, tnums in the other, the name please.')
parser.add_argument('--NewLocation', metavar = 'N', default = '/data/RECglioma/archived', type = str, nargs = 1, help = 'New location for your de-identified exam.')
parser.add_argument('--StudyName', metavar = 'S', default = 'po1_preop_recur', type = str, nargs = 1, help = "Study Identifier")
args = parser.parse_args()
bnum_tnum_csv = ''.join(args.bnum_tnum_csv)


bnum_tnum_df = getting_bnum_tnum_list(bnum_tnum_csv)
print('executing program')
for index, row in bnum_tnum_df.iterrows():
    bnum = row['bnum']
    tnum = row['tnum']
    print('bnum= '+bnum+'; tnum= '+tnum)
    try: 
        gen_biopsy_command = "generate_biopsy_mask.py "+bnum+" "+tnum
        sub.call(gen_biopsy_command, shell = True)
    except IndexError as error:  
        logger.exception('generate_biopsy_mask error for bnum='+bnum+'tnum='+tnum)
        print(error)