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
import csv


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
    # EXAMPLE: batch_check_for_pattern.dev.py --csv_name txe_clin_scan_list_old.csv --cohort_name po1_preop_recur 
    #                               --output_file txe_clin_scan_list_old_notesPaula.csv --output_dir ./
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
    diffusion_pattern_file = open(output_file,"w+")
    diffusion_pattern_file.close()

    #####################################
    #   Iterating through the scans to look at each biopsy and QC it
    #####################################
    with open(output_file, "a") as diffusion_pattern_file: 
        diffusion_pattern_fileWriter = csv.writer(diffusion_pattern_file)
        for index, row in bnum_tnum_df.iterrows():
            bnum = row['bnum']
            tnum = row['tnum']

            os.chdir(output_dir)

            #####################################
            #   Changing the directory to the appropriate place
            #####################################

            print('changing path to: '+recgli_path_root+bnum+"/"+tnum)
            change_path(recgli_path_root)
            #####################################
            #   Find the path to the t1ca  image 
            #####################################
            if len(glob.glob('images/*t1ca.idf'))>0: 
                print('t1ca found')
                t1ca_path = glob.glob('images/*t1ca.idf')[0]
            elif len(glob.glob('images/*t1ca.idf'))>0: 
                print('t1c (not aligned) found')
                t1ca_path = glob.glob('images/*t1c.idf')[0]
            else: 
                print('no t1ca or t1c image found')
                t1ca_path = None


            #####################################
            #   Find the path to the adca 1000 image 
            #   (adc 2000 image if alignment not available)
            #####################################
            if len(glob.glob('diffusion_b=1000/*adca.idf'))>0: 
                print('adca 1000 found')
                adca_path = glob.glob('diffusion_b=1000/*adca.idf')[0]
            elif len(glob.glob('diffusion_b=2000/*adca.idf'))>0: 
                print('adca 2000 found')
                adca_path = glob.glob('diffusion_b=2000/*adca.idf')[0]
            elif len(glob.glob('diffusion_b=1000/*adc.idf'))>0: 
                print('adc 1000 found')
                adca_path = glob.glob('diffusion_b=2000/*adc.idf')[0]
            elif len(glob.glob('diffusion_b=2000/*adc.idf'))>0: 
                print('adc 2000 found')
                adca_path = glob.glob('diffusion_b=2000/*adc.idf')[0]
            else: 
                print('no adca or adc image found')
                adca_path = None

            change_path(recgli_path_root)

            #####################################
            #  
            #####################################
            if t1ca_path != None and adca_path != None: 
                print('Loading T1c and ADCa overlay.')
                #####################################
                #   Define command, call the command, and annotate the biopsy. Write this out in the file.
                #####################################
                view_adca_overlay_command = 'sivic -i '+t1ca_path+ ' -i '+adca_path
                
                sub.call(view_adca_overlay_command, shell = True)
                
                pattern_exists = input('Does Paulas pattern exist? (y/n/m): ')
                ring_enhancement_exists = input('Is there ring enhancement? (y/n/m): ')
                notes = input('Additional notes?: ')
                
                diffusion_pattern_file_line = [bnum, tnum, pattern_exists, ring_enhancement_exists, notes]


            elif t1ca_path==None: 
                print('ERROR! No t1c image for '+bnum+' ,'+tnum+', writing that to file.')

                diffusion_pattern_file_line = [bnum, tnum, 'no_t1c_image']
            else: 
                print('ERROR! No diffusion for '+bnum+' ,'+tnum+', writing that to file.')

                diffusion_pattern_file_line = [bnum, tnum, 'no_diffu_image']
                
            print(diffusion_pattern_file_line)

            diffusion_pattern_fileWriter.writerow(diffusion_pattern_file_line) 


