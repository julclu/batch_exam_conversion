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

## in this script we want to 
## 0. Create the argument parser
## 1. import all of the bnums and tnums n 

########### Create an argument parser 
print('creating argument parser')
parser = argparse.ArgumentParser(description='In this script we will import a single bnum/tnum, run the archive_exam perl script, and then dcm_qr to desired location.')
parser.add_argument('bnum_tnum_csv', type=str, nargs=1, help='List of bnums in one column, tnums in the other, the name please.')
parser.add_argument('--output_file_name', type=str, nargs=1, default = "valid_perfusion_record.csv", help='Name of the file that youd like to write to.')
parser.add_argument('--output_file_directory', type=str, nargs=1, default = "/home/sf673542/preop_convert_work", help='Path to the directory that youd like to write to.')
#parser.add_argument('--old_po1', type = bool, nargs =1, default = False)
parser.add_argument('--old_po1', help='Flag if from old_po1', action='store_true')
# args = parser.parse_args('po1_preop_recur_bnum_tnum_list1.10.csv --old_po1'.split())
args = parser.parse_args()

########### Defining the arguments 
bnum_tnum_csv = ''.join(args.bnum_tnum_csv)
output_file_name = "".join(args.output_file_name)
output_file_directory = ''.join(args.output_file_directory)
old_po1 = args.old_po1

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
if old_po1 == True: 
    recgli_path_root = "/data/RECglioma/archived/"
else: 
    recgli_path_root = '/data/RECglioma/'

print('executing program')
for index, row in bnum_tnum_df.iterrows():
    bnum = row['bnum']
    tnum = row['tnum']
    print('bnum= '+bnum+'; tnum= '+tnum)
    print('changing path to: '+recgli_path_root+bnum+"/"+tnum)
    change_path(recgli_path_root)
    ## find the path of the first 
    if len(glob.glob('*/*firsta.idf'))>1: 
        first_path = glob.glob('*/*firsta.idf')[0]
    elif len(glob.glob('*/*first.idf'))>1: 
        first_path = glob.glob('*/*first.idf')[0]
    else: 
        first_path = None

    ## find the name of the ROIs to overlay 
    tnum_dirs = os.listdir()
    if "roi_analysis" in tnum_dirs: 
        os.chdir('roi_analysis')
        vial_files = glob.glob('*_t1ca_*.idf')
    else: 
        vial_files = []

    change_path(recgli_path_root)
    ## define command:
    if first_path != None: 
        print('defining command for viewing biopsy')
        if len(vial_files)==0: 
            svk_quick_view_command = 'svk_multi_view '+first_path
        else: 
            svk_quick_view_command = 'svk_multi_view '+first_path+" --skipValidation"
            for vial in vial_files: 
                svk_quick_view_command = svk_quick_view_command+" -n roi_analysis/"+vial

        print('Look through perfusion to see if fully blood:')
        print('There should be ', len(vial_files), ' biopsies')
        sub.call(svk_quick_view_command, shell = True)
        valid_perf = input('Is the perfusion image valid? y/m/n: ')
        change_topup = input('Should the perf be reprocessed? y/n/m/na: ')
        notes = input('Additional notes?: ')
        if valid_perf == "y" or valid_perf == "n" or valid_perf == "m":
            if change_topup == "y" or change_topup == "n" or change_topup =="na" or change_topup=="m": 
                perf_valid_file = open('perf_valid_file.csv',"w+") 
                perf_valid_file.write(bnum+","+tnum+","+valid_perf+","+change_topup+","+notes)
                perf_valid_file.close()
            else:
                print('error: please input y for yes, n for no, or na for not applicable.')
                valid_perf = input('Should the perf be reprocessed without topup y/n/na: ')
        else: 
            print('error: please input y for yes, n for no, or m for maybe.')
            valid_perf = input('Is the perfusion image valid? y/m/n: ')
    else: 
        print("No perfusion! Logging that in perf_valid_file.csv")
        perf_valid_file = open('perf_valid_file.csv',"w+") 
        perf_valid_file.write(bnum+","+tnum+", no_perf")
        perf_valid_file.close()


