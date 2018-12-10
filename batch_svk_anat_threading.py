#!/usr/bin/env python

import os
import glob
import argparse 
import subprocess as sub
import shlex 
from subprocess import PIPE, Popen
import pandas as pd
import threading as t 
import datetime

def getting_bnum_tnum_list(csv_file): 
    ########### Get bnum_tnum list: 
    savedir = os.getcwd()
    os.chdir(csv_dir)
    bnum_tnum_df = pd.read_csv(csv_file, header = None)
    bnum_tnum_df.columns = ['bnum', 'tnum', 'DUMMY']
    os.chdir(savedir)
    return bnum_tnum_df
    
def threading_function(mystring):	
	print(mystring+str(datetime.time))


# parser = argparse.ArgumentParser(description='Importing a bnum, tnum list & performing svk_roi_analysis on its anatomical images.')
# parser.add_argument('--csv_file', '-c',  required = True, help = 'CSV file with bnums and tnums list, please no "b" or "t"')
# parser.add_argument('--csv_dir',  '-d',  required = True, help = 'Exact path to the CSV file')

# args = parser.parse_args()

# csv_file = args.csv_file
# csv_dir = args.csv_dir

# print("=============================")
# print("CSV file name = ", csv_file)
# print("CSV dir name  = ", csv_dir)
# print("=============================")

# bnum_tnum_df = getting_bnum_tnum_list(csv_file)

# for index, row in bnum_tnum_df.iterrows():
#     bnum = row['bnum']
#     tnum = row['tnum']
#     print('bnum= '+bnum+'; tnum= '+tnum)
#     try: 
#         anat_svk_command = 'svk_roi_analysis -t '
#     	t.start_new_thread()
#         sub.call(convert_exam_command, shell = True)
#     except Exception as error:  
#         print('convert_exam or align_intra error for bnum='+bnum+'tnum='+tnum)
#         print(error)

# function perform_row

for i in range(0,100): 
	try:
		# command = get_command
		# perform_command(command)
	   t.start_new_thread( threading_function, ("Thread-1", ) )
	   t.start_new_thread( threading_function, ("Thread-2", ) )
	except:
	   print("Error: unable to start thread")