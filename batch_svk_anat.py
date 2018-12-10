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

def getting_bnum_tnum_list(csv_dir, csv_name): 
    ########### Get bnum_tnum list: 
    savedir = os.getcwd()
    os.chdir(csv_dir)
    bnum_tnum_df = pd.read_csv(csv_name, header = None)
    bnum_tnum_df.columns = ['bnum', 'tnum', 'DUMMY']
    os.chdir(savedir)
    return bnum_tnum_df

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='Create logger of when svk_roi_analysis for anatomical quantification fails.')
    parser.add_argument("--csv_name",        required=True,    help='Precise name of the csv file that contains the perfusion files of interest.')
    parser.add_argument("--csv_dir",         required=True,    help='Precise path of the csv file that contains the perfusion files of interest.')
    parser.add_argument("--cohort_name",     required=True,    help='Precise cohort name of the scans of interest (e.g. "po1_preop_recur" or "REC_HGG")')

    args = parser.parse_args()
    #####################################
    #   Create strings of the arguments for 
    #   navigating to correct directory
    #####################################
    cohort_name        = args.cohort_name
    csv_name           = args.csv_name
    csv_dir            = args.csv_dir

    print("===============================================")
    print("scan list dir:     ", csv_dir)
    print("scan list name:    ", csv_name)
    print("cohort name:       ", cohort_name) 
    print("===============================================")

    bnum_tnum_df = getting_bnum_tnum_list( csv_dir, csv_name)

    #==========================================
    # Instantiate error log data frame
    #==========================================
    error_log = pd.DataFrame()

    for index, row in bnum_tnum_df.iterrows():
        bnum = row['bnum']
        tnum = row['tnum']
        #==========================================
        # Fixing Naming Errors
        #==========================================
        if len(bnum)==4: 
            bnum = bnum[0:1]+'0'+bnum[1:len(bnum)]

        error_log_line = {'bnum': bnum, 'tnum': tnum}
        print(bnum)
        print(tnum)
        
        #==========================================
        # setting cohort root 
        #==========================================

        try: 
            if cohort_name == "REC_HGG": 
                cohort_root = '/data/RECglioma/'
            elif cohort_name == "po1_preop_recur":
                cohort_root = '/data/RECglioma/archived/'
            else: 
                print("ERROR! please input valid cohort name.")
        except: 
            print("ERROR! please input valid cohort name")
        
        os.chdir(cohort_root)
        
        #==========================================
        # Switch into correct directory if possible
        #==========================================
        if bnum in glob.glob("*"): 
            os.chdir(bnum)
            if tnum in glob.glob('*'): 
                os.chdir(tnum)
                #==========================================
                # Setting status codes 0 go 1 stop
                #==========================================
                status_code = 0
            else: 
                print('Scan not in patient directory.')
                status_code = 1
                error_log_line['no_tnum']='scan_not_in_bnum'
        else:
            print('Patient not in cohort.')
            status_code = 1
            error_log_line['no_bnum']='patient_not_in_cohort'
        
        #==========================================
        # Figure out if we have sfnum, t1va file; 
        # if not, we don't want to go ahead and 
        # reprocess for this cohort:
        #==========================================
        if len(glob.glob('sf*'))>0: 
            sfnum = glob.glob('sf*')[0]
            sfnum = sfnum[2:]
        else: 
            status_code = 1
            error_log_line['no_sfnum']='no_screenshots'
        if len(glob.glob('images/*t1va.idf'))>0: 
            command = 'svk_roi_analysis.dev -'+tnum+' -s'+sfnum+' --quant anat'
        else: 
            status_code = 1
            error_log_line['no_t1va']='No_reprocessing_necessary'
        
        #==========================================
        # Figure out if the code has already run so 
        # as not to run it again: 
        #==========================================
        # with open('Logfile') as logfile: 
        #     logfile_lines = logfile.readLines()

        #==========================================
        # If status_code = 0, we can go ahead and 
        # try to reprocess for correct value of t1d
        #==========================================
        if status_code ==0: 
            try:
                sub.call(command, shell = True)
            except OSError as err:
                print("OS error: {0}".format(err))
                error_log_line['os_error']='os_error'
            except ValueError:
                print("Could not convert data to an integer.")
                error_log_line['value_error']='value_error'
            except:
                print("Unexpected error:", sys.exc_info()[0])
                error_log_line['unexp_error']='error!'
                raise

        error_log = error_log.append(error_log_line, ignore_index = True)
    
    error_log.to_csv('error_log_batch_svk_roi_anat.csv')