# This script takes the following as inputs passed when being called,
# path of electrode coordinates .xlsx file
# path of file containing electrode coordinates in anatomical space
# path of comb_matched array, and
# generates a report (.txt) which compares the detected electrodes (comb_matched)
# with those in the dataset (.xlsx)
#----------------------------------------------------------------------------------

import os
import re
import sys
import pandas as pd
import numpy as np
from prelim_setup import get_path, sort_elect, mni2ijk, get_elect_contact_ijk

#--------------------------------------------------------------------------
# Part (I): read paths of input files required from arguments passed when the
# script is called

# 1st arg. = path of electrode coordinates .xlsx file
# 2nd arg. = path of file containing electrode coordinates in anatomical space
# 3rd arg. = path of comb_matched array

# obtain paths of files required through arguments passed when the script is called
elect_file_path = sys.argv[1]
elect_coord_anat_file_path = sys.argv[2]
comb_matched_file_path = sys.argv[3]

# END Part (I): read paths of input files required from arguments passed when the
# script is called
#--------------------------------------------------------------------------

# Part (II): Read info. about electrode dataset and comb. detected input files

# load electrode coordinates from .xlsx file into dataframe,
# selected only first 4 columns
elect_df = pd.read_excel(elect_file_path, usecols=list(range(5)))

# elect_ijk_all shows coordinates in mni space
# use sort_elect to sort electrode array by their types
elect_sorted = sort_elect(elect_df)

# load elect. coordinates in anat. space form input file
elect_ijk_anat_array = np.loadtxt(elect_coord_anat_file_path)

# round each entry to nearest int. and convert to list
elect_ijk_anat = elect_ijk_anat_array.round().tolist()

# read comb_matched as nested list
comb_matched = np.load(comb_matched_file_path, allow_pickle = True).tolist()

# END Part (II): Read info. about electrode dataset and comb. detected input files
# --------------------------------------------------------------------------

# Part (III): Compute metrics for the report

# sort elect_ijk_anat into groups
elect_ijk_anat_sorted = []
row_num = 0
for group in elect_sorted:
    curr_group_ijk = []
    for i in range(len(group)):
        curr_group_ijk.append(elect_ijk_anat[row_num])
        row_num = row_num + 1
    elect_ijk_anat_sorted.append(curr_group_ijk)

# get electrode name for every group of electrodes
elect_gp_name = []
for group in elect_sorted:
    name_tag = group[0][0]
    gp_name = re.search('[a-zA-Z]+', name_tag).group()
    elect_gp_name.append(gp_name)

# define function find_group() to find the corresponding ground truth
# coordinates for every contact identified in comb_matched
# return counter = 0 if no matching ground truth is found
def find_group(comb_input, elect_ijk_anat_sorted):
    #
    comb_int = comb_input[:]
    center_list = []
    for item in comb_int:
        center_list.append(item[3])
    #
    ind_req = 0
    counter = 0
    for item in center_list:
        #print('testing each item in center_list')
        for group_ind in range(len(elect_ijk_anat_sorted)):
            #print('testing each group in ground truth')
            for entry in elect_ijk_anat_sorted[group_ind]:
                dist = np.linalg.norm(np.array(item) - np.array(entry))
                if dist <= 4:
                    ind_req = group_ind
                    counter = 1
                    #print('found group')
                    break
            if counter != 0:
                break
        if counter != 0:
            break
    #
    return counter, ind_req

# sort electrodes in comb_matched into the following
comb_found = []   # comb with contacts found in elect dataset (A)
elect_ijk_gp_found = []   # elect with contacts detected (B)
elect_ijk_gp_found_ind = []   # indices of (B) found in elect_ijk_anat_sorted
comb_not_found = []   # comb with no contacts found in elect dataset (C)
comb_not_found_ind = []   # indices of (C) in comb_matched
elect_ijk_gp_not_found = []   # elect with no contacts detected (D)
elect_ijk_gp_not_found_ind = []   # indices of (D) in elect_ijk_anat_sorted
for comb in comb_matched:
    #
    counter, ind_req = find_group(comb, elect_ijk_anat_sorted)
    if counter == 1:
        comb_found.append(comb)
        elect_ijk_gp_found.append(elect_ijk_anat_sorted[ind_req])
        elect_ijk_gp_found_ind.append(ind_req)
    else:
        comb_not_found.append(comb)
#
for i in range(len(comb_matched)):
    if comb_matched[i] not in comb_found:
        comb_not_found_ind.append(i)
#
for i in range(len(elect_ijk_anat_sorted)):
    if elect_ijk_anat_sorted[i] not in elect_ijk_gp_found:
        elect_ijk_gp_not_found.append(elect_ijk_anat_sorted[i])
        elect_ijk_gp_not_found_ind.append(i)

# define function count_entries() to count number of entries in
# a nested list
def count_entries(comb_matched_input):
    #
    count = 0
    for comb in comb_matched_input:
        for item in comb:
            count = count + 1
    #
    return count

nc_found = count_entries(comb_matched)   # num. of contacts detected
n_tp = count_entries(comb_found)   # num. of true positives
n_fp = count_entries(comb_not_found)   # num. of false positives

# END Part (III): Compute metrics for the report
# --------------------------------------------------------------------------

# Part (IV): Generate report

# assemble path at which report is saved
report_output_dir = os.path.dirname(comb_matched_file_path)
report_filename = 'summary_analysis.txt'
report_path = os.path.join(report_output_dir, report_filename)

f = open(report_path, 'w')
print('------------------------------------------', file=f)
print('path = ', report_output_dir, file=f)
print('no. of electrodes in dataset = ', len(elect_ijk_anat_sorted), file=f)
print('no. of elect. with contacts detected = ', len(comb_found), file=f)
print('no. of elect. with no contacts detected = ', len(elect_ijk_gp_not_found), file=f)
print('no. of comb. found = ', len(comb_matched), file=f)
print('no. of comb. found with no matched elect. in dataset = ', len(comb_not_found), file=f)
print('no. of contacts detected = ', nc_found, file=f)
print('no. of contacts in dataset = ', len(elect_ijk_anat), '---(A)', file=f)
print('no. of true positives = ', n_tp, '---(B)', file=f)
print('no. of false positives = ', n_fp, '---(C)', file=f)
print('B/A = ', np.around(n_tp/len(elect_ijk_anat), 3), file=f)
print('C/A = ', np.around(n_fp/len(elect_ijk_anat), 3), file=f)
f.close()

# END Part (IV): Generate report
# --------------------------------------------------------------------------
