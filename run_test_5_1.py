# This run script uses matching algo. provided in 'ec_detect_5_1.py'
#
import time
import sys
import numpy as np
import ec_detect_5
import ec_detect_5_1
from parameter import *

# update path of directory required using 1st argument passed
# when calling this script
directname = sys.argv[1] + "/"

#
suffix_str = ''
if directname[-2] == '1':
    suffix_str = ''
elif directname[-2] == '2':
    suffix_str = '_mz'
elif directname[-2] == '3':
    suffix_str = '_standard'
elif directname[-2] == '4':
    suffix_str = '_min_max_norm'
#
w_1_path = directname + w_1_filename.replace('.npy', suffix_str + '.npy')
ncc_path = directname + ncc_filename.replace('.npy', suffix_str + '.npy')
comb_matched_path = directname + comb_matched_filename
bbox_matched_path = directname + bbox_matched_filename
#
print(w_1_path)
print(ncc_path)
print(comb_matched_path)
print(bbox_matched_path)
#
def execute():
    #
    global ncc_thresh_perct
    #
    ti = time.time()
    #
    print('w_1 path = ' + w_1_path)
    print('ncc path = ' + ncc_path)
    # print('eps_collinear = ', eps_collinear)

    w_1 = np.load(w_1_path, allow_pickle=True)  # np array w_1
    ncc = np.load(ncc_path, allow_pickle=True)  # np array ncc
    #
    bbox_matched = []
    comb_matched = []
    comb_pot = []
    #
    comb_matched, bbox_matched, comb_pot = ec_detect_5_1.matching_algo(w_1, ncc, comb_matched, bbox_matched, comb_pot,
                                                           ncc_thresh_perct, num_elect_max, radius_search_vol,
                                                           eps_collinear,
                                                           eps_dist, dist_thresh, num_contacts_max,
                                                           num_contacts_min, search_radius)
    #
    np.save(comb_matched_path, np.array(comb_matched, dtype=object))
    np.save(bbox_matched_path, np.array(bbox_matched, dtype=object))
    #
    print('done executing')
    #
    # get time elapsed, print it in unit of minutes
    elapsed = time.time() - ti
    print('time elapsed = ', elapsed / 60, 'min')

if __name__ == '__main__':
    execute()


