#!/data/svcf/software/anaconda3/bin/python


import os
import sys
import numpy as np 
import sklearn as skl 
import pandas as pd
import json
from collections import namedtuple
import glob
from sklearn.metrics import confusion_matrix
import argparse


########### Defining how to create a data frame of interesting information from a JSON file 
def create_predictions_df_from_json(dirname):
    '''
    Create a list of the predicted contrast classes in dirname
    '''
    
    ## find filename or return: 
    json_pattern = dirname + "/contrast_classifier_out/*.json"
    filename = glob.glob( json_pattern ) 
    if ( len(filename)  == 0 ):
        print("WARN: json file doesn't exist ", json_pattern)
        return
    
    ## open the file: 
    if os.path.isfile(filename[0]):
        with open(filename[0], 'r') as f:
            json_file = json.load(f)
    else: 
        print("WARN: file doesn't exist: ",  filenamne[0] )
    
    ## save the json file's key under exam as exam_uid_key:
    exam_uid_key = list(json_file['Exams'].keys())
    
    ## save json file series key: 
    series_keys = list(json_file['Exams'][exam_uid_key[0]]['Series'].keys())
    
    ## loop through series_keys to get 'contrast' description out:
    listoflists_extract_info = []
    for i in range(0, len(series_keys)): 
        contrast_output = json_file['Exams'][exam_uid_key[0]]['Series'][series_keys[i]]['Contrast']
        patientID = series_keys[i].split("/")[8]
        examID = series_keys[i].split("/")[9]
        examNum = series_keys[i].split("/")[10]
        series_ID = str(patientID+"_"+examID+"_"+examNum)
        series_summary = [series_ID, patientID, examID, examNum, contrast_output]
        listoflists_extract_info.append(series_summary)
        
    ## create the df:
    prediction_extracted_df = pd.DataFrame(listoflists_extract_info, columns = [
        'seriesID','patientID', 'examID', 'seriesNum', 'pred_contrast'])
    
    ## coding valuable labels:
    #   Assing a code (0 or 1) to each series with 1 if the value is a target class, or 0 if 'other or NA' class
    valuable_labels = ['PD', 'T2', 'T2_FLAIR', 'T1']
    preds_coded = [1 if entry in valuable_labels else 0 for entry in prediction_extracted_df['pred_contrast']]
    preds_coded = pd.DataFrame(preds_coded, columns = ['preds_coded'])
    
    ## joining the coded variable with the data frame: 
    prediction_extracted_df = prediction_extracted_df.join(preds_coded)
    
    return prediction_extracted_df



if __name__ == '__main__':

    #####################################
    # EXAMPLE: create_confusion_matrix.py --model_name SVMMetaORPixBothTypesModel_norm --cohort_name MSB_TRIAL_LABELLED 
    #                               --predictions_dir /data/svcf/predictions --output_dir ./
    #####################################
    parser = argparse.ArgumentParser(description='This script will be used to create a confusion matrix given the model name and cohort name.')
    parser.add_argument("--model_name",      required=True,    help='The precise name of the model whose confusion matrix is desired.')
    parser.add_argument("--cohort_name",     required=True,    help='The precise cohort name whose confusion matrix is desired.')
    parser.add_argument("--predictions_dir", required=True,    help="Path to model specific predictions (contains model_name/cohort_name sub-dir with prediction results) ")
    parser.add_argument("--output_dir",      required=True,    help="Path where output files get written ")
    parser.add_argument("--labels_csv",      required=False,   help="Path to labels csv file -> gold standard labels for cohort")
    parser.add_argument("-v", "--verbose",                     help = "verbose output", action='store_true', default=False,   required=False)
    args = parser.parse_args()


    #####################################
    #   Create strings of the arguments for 
    #   navigating to correct directory
    #####################################
    cohort_name     = args.cohort_name
    model_name      = args.model_name
    predictions_dir = args.predictions_dir
    output_dir      = args.output_dir
    preds_path_name = os.path.join(predictions_dir, model_name, cohort_name) 
    labels_csv      = "/data/svcf/labels/" + cohort_name  + "/labels.csv"
    if args.labels_csv != None: 
        labels_csv  = args.labels_csv 

    print("===============================================")
    print("predictions_path:  ", preds_path_name) 
    print("gold labels:       ", labels_csv) 
    print("output dir:        ", output_dir)
    print("===============================================")

    #   Write cmd to Logfile 
    cmd_string = ' '.join(sys.argv)
    with open("Logfile", "a") as logfile:
        logfile.write( cmd_string )
        logfile.write( '\n' )


    #####################################
    #   Parse the prediction dir for the mse sub-dirs 
    #####################################
    mse_nums = glob.glob(preds_path_name + '/mse*') 
        

    #####################################
    #   Create data frame of contrast class 
    #   predictions for all mse nums 
    #####################################
    preds_df = pd.DataFrame()

    # loop through all mse_nums & append to total DF 
    for mse in mse_nums: 
        #print("MSE: ", mse)
        if os.path.isdir(mse):
            dirname_df = create_predictions_df_from_json(mse)
            print(dirname_df)
            preds_df = preds_df.append(dirname_df)

    with pd.option_context('display.max_rows', None, 'expand_frame_repr', False):
        print("preds_df") 
        #print(preds_df) 
        print( preds_df[['seriesID', 'pred_contrast']])



    #####################################
    #   Read in ground truth labels 
    #####################################
    groundtruth = pd.read_csv(labels_csv, index_col = False, keep_default_na=False)
    with pd.option_context('display.max_rows', None, 'expand_frame_repr', False):
        print("truth_df") 
        #print(groundtruth) 
        print( groundtruth[['seriesID', 'HeuristicPred_contrast', 'GroundTruth_contrast']]  )


    #####################################
    #   Merge the ground truth labels with 
    #   the predictions: 
    #####################################
    merged_df = pd.merge(left = groundtruth, right = preds_df, how = "right", on = "seriesID")
    #print("MERGED: ")
    #print(merged_df)
    #print()
           

    #####################################
    #   Make sure the correct types of 
    #   columns are in the data frame: 
    #####################################
    merged_df["pred_contrast"] = merged_df['pred_contrast'].astype('str')
    merged_df["GroundTruth_contrast"] = merged_df['GroundTruth_contrast'].astype('str')
    #print("pred_contrast   gt_contrast")
    #print(merged_df["pred_contrast"] + " " +  merged_df["GroundTruth_contrast"])


    ############################################################### 
    #   Create the Confusion Matrix & percentage confusion matrix
    ############################################################### 
    conf_matrix = confusion_matrix(
        merged_df["GroundTruth_contrast"], 
        merged_df["pred_contrast"], 
        labels=["T1", "T2_FLAIR", "T2", "PD", "OTHER", "NA"]
    ) 


    #####################################
    #   rows are gt class labels 
    #   columns are actual prediction 
    #   counts for each class
    #####################################
    row_labels    = ["T1_gt", "T2_FLAIR_gt", "T2_gt", "PD_gt", "OTHER_gt", "NA_gt"] 
    column_labels = ["T1_pred", "T2_FLAIR_pred", "T2_pred", "PD_pred", "OTHER_pred", "NA_pred"]
    conf_matrix_df = pd.DataFrame(
        conf_matrix, 
        index   = row_labels,  
        columns = column_labels
    )

    #####################################
    #   Percent confusion matrix: 
    #####################################
    division_vector = conf_matrix.sum(axis=1)[:, None]
    if args.verbose == True:     
        for index, value in np.ndenumerate(division_vector):
            print("%-12s:  %-10s" % (row_labels[index[0]], value))
            #print(row_labels[index], value)
    percent_matrix = (conf_matrix / division_vector)*100
    np.set_printoptions(suppress=True)
    percent_matrix = percent_matrix.round(2)
    percent_matrix_df = pd.DataFrame(
        percent_matrix, 
        index   = row_labels,  
        columns = column_labels
    )

    #####################################
    #   Writing out files: 
    #####################################
    fname_root =  output_dir + "/" + cohort_name + '_' +  model_name 

    #####################################
    #   Preds
    #####################################
    preds_df.to_csv(         fname_root + '_predictions.csv') 
    with open (fname_root + '_predictions.txt', 'w') as f:
        f.write(preds_df.to_string())
        f.write("\n") 

    #   Counts
    conf_matrix_df.to_csv(   fname_root + '_confMatrix_counts.csv')
    with open (fname_root + '_confMatrix_counts.txt', 'w') as f:
        f.write(conf_matrix_df.to_string())
        f.write("\n") 

    #   Percentages
    percent_matrix_df.to_csv(fname_root + '_confMatrix_percentages.csv')
    with open (fname_root + '_confMatrix_percentages.txt', 'w') as f:
        f.write(percent_matrix_df.to_string())
        f.write("\n") 
