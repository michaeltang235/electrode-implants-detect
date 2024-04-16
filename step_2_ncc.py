#------------------------------------------
# This script takes the following as input arguments passed when being called,
# 1st arg. = path of w_1 file
# 2nd arg. = path of anatomical image, and
# generates ncc array that is saved under the same directory of the w_1 file

# note: different w_1 file is used based on the normalization method used
# when the w_1 file was made (i.e. exp number)
#------------------------------------------

import os
import sys
import numpy as np
import nibabel as nib
import ec_detect

print('done loading packages')

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

#--------------------------------------------------------------------------
# Part (I): read paths of input files required from arguments passed when the
# script is called

# 1st arg. = path of w_1 from sub. 27
# 2nd arg. = path of anatomical image in scanner space

# obtain paths of files required through arguments passed when the script is called
w_1_file_path = sys.argv[1]
anat_img_file_path = sys.argv[2]

print(w_1_file_path)
print(anat_img_file_path)

# END Part (I): read paths of input files required from arguments passed when the
# script is called
#--------------------------------------------------------------------------

# load w_1 array using path input
w_1 = np.load(w_1_file_path, allow_pickle = True)   # np array w_1

# load anat. img by first creating instance of the variable,
# then access the image data
anat_inst = nib.load(anat_img_file_path)
anat_img = anat_inst.get_fdata()  # actual image data
#anat_header = anat_inst.header  # metadata about the image

# format search_img by taking transpose on the anat. img,
# then apply w_1 loaded onto search_img to get ncc array at every translation
search_img = np.transpose(anat_img, axes=[1, 0, 2])
ncc, _, _, _, _ = ec_detect.compute_ncc(w_1, search_img)

# format output path of ncc array (ncc array is saved under the same directory
# as the w_1 template loaded
ncc_output_dir = os.path.dirname(w_1_file_path) + '/'
ncc_filename = 'ncc.npy'

# format suffix of ncc filename to reflect the normalization method used when
# making the w_1 template, as well as the experiment number
suffix_str = ''
if ncc_output_dir[-2] == '1':
    suffix_str = ''
elif ncc_output_dir[-2] == '2':
    suffix_str = '_mz'
elif ncc_output_dir[-2] == '3':
    suffix_str = '_standard'
elif ncc_output_dir[-2] == '4':
    suffix_str = '_min_max_norm'

# save ncc to path formatted above
ncc_path = ncc_output_dir + ncc_filename.replace('.npy', suffix_str + '.npy')
np.save(ncc_path, ncc)

print('done computing ncc array')
