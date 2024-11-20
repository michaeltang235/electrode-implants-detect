
#------------------------------------------
# This version, compared to '5_1',
# - allows normalization of image cropped before computing an average
# template w_1
# - removes the part that computes ncc array, which is moved to another
# script 'step_2_ncc.py'
#
# w_1 = w_1 without norm.
# w_1_mz = w_1 obtained using mean-zero norm. of every image subset
# w_1_standard =  w_1 obtained using standardization of every image subset
# w_1_min_max_norm = w_1 obtained using min-max norm. of every image subset

#------------------------------------------


import os
import re
import pandas as pd
import numpy as np
#from scipy import ndimage
#from sklearn.cluster import DBSCAN
#from skimage.transform import resize
#from scipy.signal import welch
#import itertools
import nibabel as nib

from prelim_setup import get_path, sort_elect, mni2ijk, get_elect_contact_ijk
import ec_detect
#import ec_detect_2
import ec_detect_5

import matplotlib.pyplot as plt

#import pickle

import time

print('done loading packages')

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# BEGIN USER INPUT

# enter subject number (str)
subnum = '27'

# enter experiment series label (str)
exp_label = 'b'

# enter path to directory where all input files are located
#directname = 'C:\\Users\\siumichael.tang\\Downloads\\elect_locate\\' + 'sub' + subnum
directname = '/work/levan_lab/mtang/elect_locate/' + 'sub' + subnum

# format filenames input files required
filename_anat_img = '^re_3.*\.nii$'  # fsl-resampled anatomical images
filename_elect = subnum + '_.*Koordinaten.*\.xlsx'  # file containing mni coord. of all electrode pairs
filename_elect_coord_anat = 'elect_contacts_coord_anat.txt'   # file containing elect. coord. in anat. space

# format output directory
directname_op = directname + '/data_py/jul15_2024'

# END USER INPUT
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# use get_path function to obtain full path of input files
anat_file_path = get_path(directname + '/fsl_resample', filename_anat_img)  # unprocessed anat. images
elect_file_path = get_path(directname, filename_elect)  # file containing info. about electrodes coordinates
elect_coord_anat_file_path = get_path(directname + '/fsl_resample', filename_elect_coord_anat)    # file containing info. about elect. coord. in anat. space

# create instance of processed image
anat_inst = nib.load(anat_file_path[0])
anat_img = anat_inst.get_fdata()  # actual image data
anat_header = anat_inst.header  # metadata about the image

# load electrode coordinates from .xlsx file into dataframe,
# selected only first 4 columns
elect_df = pd.read_excel(elect_file_path[0], usecols=list(range(5)))

# ---------------------------------------------------------------------------
# Part (II): sort electrodes by their types and obtain their image space
# coordinates

# elect_ijk_all shows coordinates in mni space
# use sort_elect to sort electrode array by their types
elect_sorted = sort_elect(elect_df)
_, elect_ijk_all = get_elect_contact_ijk(elect_sorted, anat_header)

# load elect. coordinates in anat. space form input file
elect_ijk_anat_array = np.loadtxt(elect_coord_anat_file_path[0])

# round each entry to nearest int. and convert to list
elect_ijk_anat = elect_ijk_anat_array.round().tolist()

print('done loading saved variables')

# END Part (II): sort electrodes by their types and obtain their image space
# coordinates
# ---------------------------------------------------------------------------

# Part (III): select reference image, on which other images are mapped

# select reference image as first electrode contact,
# manually adjust coordinates to capture entire artifact
ad_x = 1   # manual adjustment in x
ad_y = 0   # manual adjustment in y
ad_z = 0   # manual adjustment in z
x_coor_ref = int(elect_ijk_anat[0][0]) - 1 + ad_x
y_coor_ref = int(elect_ijk_anat[0][1]) - 1 + ad_y
z_coor_ref = int(elect_ijk_anat[0][2]) - 1 + ad_z
spac_ref = 3   # spacing in each direction

# crop out portion enclosing the entire electrode contact
ref_img = np.transpose(anat_img[x_coor_ref - spac_ref:x_coor_ref + spac_ref + 1:1, \
                               y_coor_ref - spac_ref:y_coor_ref + spac_ref + 1:1, \
                       z_coor_ref - spac_ref:z_coor_ref + spac_ref + 1:1],
                               axes = [1, 0, 2])

# plot ref image to check manual selection, with red 'x' to denote the
# center of the template
# plt.imshow(ref_img[:, :, spac_ref], cmap='gray', origin='lower')
# plt.scatter(spac_ref, spac_ref, c='r', marker='x')
# plt.imshow(np.transpose(anat_img[:, :, z_coor_ref]), cmap='gray', origin='lower')
#
# for i in range(8):
#    x_coor_ref = int(elect_ijk_anat[20+i][0]) - 1
#    y_coor_ref = int(elect_ijk_anat[20+i][1]) - 1
#    plt.scatter(int(x_coor_ref), int(y_coor_ref), c='r', marker='.')
#
# plt.xlim([100, 200])
# plt.ylim([100, 150])
#
# plt.scatter(int(x_coor_ref), int(y_coor_ref), c='r', marker='.')



# END Part (III): select reference image, on which other images are mapped
# ---------------------------------------------------------------------------

# Part (IV): select images of electrode contacts using coordinates
# in anat. space provided in dataset

# specify spacing on each side of electrode contact
spac = 5

# compute img_sel, to store image selected at every contact in anat image
img_sel = ec_detect_5.select_img(anat_img, elect_ijk_anat, spac)

#plt.imshow(np.mean(avg_img_1, axis=2), cmap='gray', origin='lower')
#plt.imshow(np.mean(img_sel[0], axis=2), cmap='gray', origin='lower')
#plt.imshow(img_sel[0][:, :, spac], cmap='gray', origin='lower')
#plt.imshow(np.transpose(anat_img[:, :, 47]), cmap='gray', origin='lower')

#plt.imshow(np.mean(np.transpose(wanat_img, axes = [1, 0, 2]), axis=2), cmap='gray', origin='lower')
#plt.imshow(np.mean(img_sel[2], axis=2), cmap='gray', origin='lower')
#plt.imshow(np.transpose(wanat_img[:, :, 45]), cmap='gray', origin='lower')
#plt.scatter(x_coor, y_coor, c='r', marker='x')

# END Part (IV): select images of electrode contacts using coordinates
# # in anat. space provided in dataset
# ---------------------------------------------------------------------------

# Part (V): shift images to best align with reference image using
# normalized cross correlation, normalize each best-aligned image, and
# compute average shifted images (elementwise average)

# align image of every elect. contact with ref_img (max ncc is obtained),
# then normalize each best-aligned image,
# _mz = mean-zero, _standard = standardization, _min_max_norm = min-max norm,
# and compute avg. template (w_1) of the normalized best-aligned image of every
# elect. contact
w_1 = ec_detect_5.compute_w_1(ref_img, img_sel, 1)
w_1_mz = ec_detect_5.compute_w_1(ref_img, img_sel, 2)
w_1_standard = ec_detect_5.compute_w_1(ref_img, img_sel, 3)
w_1_min_max_norm = ec_detect_5.compute_w_1(ref_img, img_sel, 4)

# plot shifted image
#plt.imshow(np.mean(shifted_img[0], axis=2), cmap='gray', origin='lower')
#plt.imshow(np.mean(w_1, axis=2), cmap='gray', origin='lower')
#plt.show()   # show output

# END Part (V): shift images to best align with reference image using
# # normalized cross correlation, normalize each best-aligned image, and
# # compute average shifted images (elementwise average)
# ---------------------------------------------------------------------------
#
# Part (VI): save variables to path

w_1_path = os.path.join(directname_op + '/exp_' + exp_label + '_1', 'w_1.npy')
w_1_mz_path = os.path.join(directname_op + '/exp_' + exp_label + '_2', 'w_1_mz.npy')
w_1_standard_path = os.path.join(directname_op + '/exp_' + exp_label + '_3', 'w_1_standard.npy')
w_1_min_max_norm_path = os.path.join(directname_op + '/exp_' + exp_label + '_4', 'w_1_min_max_norm.npy')

np.save(w_1_path, w_1)
np.save(w_1_mz_path, w_1_mz)
np.save(w_1_standard_path, w_1_standard)
np.save(w_1_min_max_norm_path, w_1_min_max_norm)

# END Part (VI): save variables to path
# ---------------------------------------------------------------------------
