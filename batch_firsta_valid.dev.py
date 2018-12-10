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
import sys

## in this script we want to create a systematic logger of whether biopsies are valid or not through visual inspection: 

## This is how to create the bnum_tnum_df that we are interested in: 
def getting_bnum_tnum_list(bnum_tnum_csv): 
    ########### Get bnum_tnum list: 
    bnum_tnum_df = pd.read_csv(bnum_tnum_csv_root+bnum_tnum_csv, header = None)
    bnum_tnum_df.columns = ['bnum', 'tnum', 'DUMMY']
    return bnum_tnum_df

## This is a quick way to change to the tnum folder we're lookgng for depending on the root: 
def change_path(pathname_root):
    pathname = pathname_root+bnum+'/'+tnum
    os.chdir(pathname)

if __name__ == '__main__':

    #####################################
    # EXAMPLE: batch_firsta_valid.dev.py --csv_name po1_preop_recur_bnum_tnum_list1.10.csv --cohort_name po1_preop_recur 
    #                               --output_file po1_validBiopsies_list1.csv --output_dir ./
    #####################################

    parser = argparse.ArgumentParser(description='Create a systematic logger of whether biopsies are valid or not through visual inspection')
    parser.add_argument("--csv_name",        required=True,    help='Precise name of the csv file that contains the perfusion files of interest.')
    parser.add_argument("--csv_root",        required=True,    help='Precise path to the csv file that contains the perfusion files of interest.')
    parser.add_argument("--cohort_name",     required=True,    help='Precise cohort name of the scans of interest (e.g. "po1_preop_recur" or "RECglioma")')
    parser.add_argument("--output_file",     required=False,   help="Name of the output file csv", default = "perf_valid_file.csv")
    parser.add_argument("--output_dir",      required=True,    help="Path where output files get written ")
    parser.add_argument("-v", "--verbose",                     help = "verbose output", action='store_true', default=False,   required=False)
    args = parser.parse_args()


    #####################################
    #   Create strings of the arguments for 
    #   navigating to correct directory
    #####################################
    cohort_name        = args.cohort_name
    csv_name           = args.csv_name
    bnum_tnum_csv_root = args.csv_root
    output_file        = args.output_file
    output_dir         = args.output_dir


    print("===============================================")
    print("scan list name:    ", csv_name)
    print("cohort name:       ", cohort_name) 
    print("output file name:  ", output_file) 
    print("output dir:        ", output_dir)
    print("===============================================")

    #   Write cmd to Logfile 
    cmd_string = ' '.join(sys.argv)
    with open("Logfile", "a") as logfile:
        logfile.write( cmd_string )
        logfile.write( '\n' )

    #####################################
    #   Reading in the csv_name
    #   as the scan listls

    #####################################

    bnum_tnum_df = getting_bnum_tnum_list(csv_name)

    #####################################
    #   Setting the roots of the data 
    #   based on the cohort name
    #####################################

    if cohort_name == 'po1_preop_recur': 
        recgli_path_root = '/data/RECglioma/archived/'
    elif cohort_name == 'RECglioma': 
        recgli_path_root = '/data/RECglioma/'
    else: 
        print('Please use a valid cohort name, RECglioma or po1_preop_recur.')
        exit(1)

    #####################################
    #   Opening the output file based on
    #   the output dir and output file name 
    #####################################
    perf_valid_file = open(output_file,"w+")
    perf_valid_file.close()

    #####################################
    #   Iterating through the scans to look at each biopsy and QC it
    #####################################

    for index, row in bnum_tnum_df.iterrows():
        bnum = row['bnum']
        tnum = row['tnum']

        os.chdir(output_dir)
        perf_valid_file = open(output_file,"a")

        #####################################
        #   Changing the directory to the appropriate place
        #####################################

        print('changing path to: '+recgli_path_root+bnum+"/"+tnum)
        change_path(recgli_path_root)

        #####################################
        #   Find the path to the firsta image (first image if alignment not available)
        #####################################
        if len(glob.glob('*/*firsta.idf'))>0: 
            print('firsta found')
            first_path = glob.glob('*/*firsta.idf')[0]
        elif len(glob.glob('*/*first.idf'))>0: 
            print('first found')
            first_path = glob.glob('*/*first.idf')[0]
        else: 
            print('no perf found')
            first_path = None

        #####################################
        #   Find the nmes of the biopsies that we want to look at
        #####################################
        tnum_dirs = os.listdir()
        if "roi_analysis" in tnum_dirs: 
            os.chdir('roi_analysis')
            vial_files = glob.glob('*_t1ca_*.idf')
        else: 
            vial_files = []

        #####################################
        #   Cycle through the vial_files and overlay those on the 
        #   firsta image individually to QC independently: 
        #####################################
        change_path(recgli_path_root)

        if len(vial_files)>0 and first_path != None: 
            print('There should be '+str(len(vial_files))+' biopsies for this scan.')
            for vial in vial_files: 
                print('vial name :'+vial)
                #####################################
                #   Define command, call the command, and annotate the biopsy. Write this out in the file.
                #####################################
                view_vial_overlaid_on_perf_command = 'svk_multi_view '+first_path+ ' -n roi_analysis/'+vial+" --skipValidation"
                
                sub.call(view_vial_overlaid_on_perf_command, shell = True)
                
                biopsy_valid = input('Is this biopsy in a good place on the perfusion map? (y/n/m): ')
                
                notes = input('Additional notes?: ')
                
                perf_valid_file.write(bnum+","+tnum+","+vial+","+biopsy_valid+","+notes+"\n")

            perf_valid_file.close()

        elif len(vial_files)==0: 
            print('ERROR! No biopsies for '+bnum+' ,'+tnum+', writing that to file.')
            perf_valid_file.write(bnum+","+tnum+", no_biopsies\n")
            perf_valid_file.close()
        else: 
            print('ERROR! No perfusion for '+bnum+' ,'+tnum+', writing that to file.')
            perf_valid_file.write(bnum+","+tnum+", no_perf\n")
            perf_valid_file.close()

    perf_valid_file.close()
