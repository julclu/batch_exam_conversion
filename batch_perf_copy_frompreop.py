#!/usr/bin/env python

import os
import glob
import argparse 
import subprocess as sub
import shlex 
from subprocess import PIPE, Popen
import pandas as pd

########### Create an argument parser 
print('creating argument parser')
parser = argparse.ArgumentParser(description='In this script we will import a single bnum/tnum, run the archive_exam perl script, and then dcm_qr to desired location.')
parser.add_argument('bnum_tnum_csv', type=str, nargs=1, help='List of bnums in one column, tnums in the other, the name please.')
# args = parser.parse_args('po1_preop_recur_bnum_tnum_list1.10.csv --old_po1'.split())
args = parser.parse_args()

########### Defining the arguments 
bnum_tnum_csv = ''.join(args.bnum_tnum_csv)

## define a few functions: 
def getting_bnum_tnum_list(bnum_tnum_csv): 
    ########### Get bnum_tnum list: 
    bnum_tnum_csv_root = "/home/sf673542/preop_convert_work/"
    bnum_tnum_df = pd.read_csv(bnum_tnum_csv_root+bnum_tnum_csv, header = None)
    bnum_tnum_df.columns = ['bnum', 'tnum', 'DUMMY']
    return bnum_tnum_df

def change_path(pathname_root):
    pathname = pathname_root+bnum+'/'+tnum
    os.chdir(pathname)

bnum_tnum_df = getting_bnum_tnum_list(bnum_tnum_csv)

############# set roots
origin_path_root = "/data/bioe4/po1_preop_recur/"
destination_path_root = '/data/RECglioma/archived/'
############ 


for index, row in bnum_tnum_df.iterrows():

    bnum = row['bnum']
    tnum = row['tnum']

    if len(bnum)==5: 
        print('bnum= '+bnum+'; tnum= '+tnum)
        print('changing path to: '+origin_path_root+bnum+"/"+tnum)
        change_path(origin_path_root)
        print('copying all of the perfusion from: ', origin_path_root)
        perfusion_dirs_and_files = glob.glob('*perf*')
        bad_dirs_and_files = glob.glob('*bad*')
        temp_dirs_and_files = glob.glob('*temp*')
        bad_temp_files = bad_dirs_and_files+temp_dirs_and_files
        perfusion_dirs_and_files = [dir_and_file for dir_and_file in perfusion_dirs_and_files if dir_and_file not in bad_temp_files] 
        for dir in perfusion_dirs_and_files: 
        	copy_command = "cp -r "+dir+" "+destination_path_root+bnum+"/"+tnum
        	sub.call(copy_command, shell=True)
    else:
        bnum = bnum[0]+"0"+bnum[1:]
        print('bnum= '+bnum+'; tnum= '+tnum)
        print('changing path to: '+origin_path_root+bnum+"/"+tnum)
        change_path(origin_path_root)
        print('copying all of the perfusion from: ', origin_path_root)
        perfusion_dirs_and_files = glob.glob('*perf*')
        bad_dirs_and_files = glob.glob('*bad*')
        temp_dirs_and_files = glob.glob('*temp*')
        bad_temp_files = bad_dirs_and_files+temp_dirs_and_files
        perfusion_dirs_and_files = [dir_and_file for dir_and_file in perfusion_dirs_and_files if dir_and_file not in bad_temp_files] 
        for dir in perfusion_dirs_and_files: 
            copy_command = "cp -r "+dir+" "+destination_path_root+bnum+"/"+tnum
            sub.call(copy_command, shell=True)






