#------------------------------------------
# This version, compared to previous ones
# - first uses single-contact template to identify potential detections
# - then at each detection point, use multi-contact template with rotations
# to search for group of points that aligned with each other
# - place left end of multi-contact template on a detection point,
# - rotate, get ncc, translate 1 contact over,
# - repeat the same process, all the way to the right end of template

# This script, ec_detect_script_3.py, does single-contact template
# detection on mri image, same as before, and saves bbox_list_3 to path
# for easy procession later.

#------------------------------------------

import os
import re
import pandas as pd
import numpy as np
from scipy import ndimage
from sklearn.cluster import DBSCAN
from skimage.transform import resize
# from scipy.signal import welch
import nibabel as nib

from prelim_setup import get_path, sort_elect, mni2ijk, get_elect_contact_ijk
import ec_detect

import matplotlib.pyplot as plt

import pickle

import time

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
def step_1(img_template, ncc_array, ncc_thresh):
    # obtain indices of voxels >= threshold
    # ncc_ind[:3] = indices
    # ncc_ind[-1] = ncc
    ncc_ind = np.argwhere(ncc_array >= ncc_thresh)
    ncc_list_thresholded = []
    for item in ncc_ind:
        ncc_val_req = ncc_array[item[0], item[1], item[2]]
        ncc_list_thresholded.append([item[0], item[1], item[2], ncc_val_req])
    # transpose indices in ncc_ind, add them to centers defined by img_template
    # ecf = electrode contacts found
    # ecf[:3] = indices in image space
    # ecf[-1] = ncc at that voxel
    ecf = []
    for item in ncc_list_thresholded:
        ecf.append([int((img_template.shape[0] - 1) / 2 + item[1]),
                    int((img_template.shape[1] - 1) / 2 + item[0]),
                    int((img_template.shape[2] - 1) / 2 + item[2]), item[-1]])
    return ecf

# ---------------------------------------------------------------------------
def step_2(ecf, bbox_spac, iou_thresh):
    # construct bounding box for every detection of electrode contact
    bbox_list = []
    for item in ecf:
        bbox_para = ec_detect.define_bounding_box(item, bbox_spac)
        bbox_list.append(bbox_para)
    # remove overlapping detections with non-maximum suppression
    # iou_thresh = 0.17 for translating 2 units in each direction
    bbox_list_cleaned = ec_detect.nms(bbox_list, iou_thresh)
    return bbox_list_cleaned

# ---------------------------------------------------------------------------
def step_3(bbox_list_input, max_dist_thresh):
    bbox_list_3 = ec_detect.check_distance(bbox_list_input, max_dist_thresh)
    return bbox_list_3

# ---------------------------------------------------------------------------

def run_detect(img_template, ncc_array, ncc_thresh, bbox_spac, iou_thresh, max_dist_thresh):
    ecf = step_1(img_template, ncc_array, ncc_thresh)
    bbox_list_2 = step_2(ecf, bbox_spac, iou_thresh)
    bbox_list_3 = step_3(bbox_list_2, max_dist_thresh)
    return bbox_list_3


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# BEGIN USER INPUT

# enter subject number (str)
subnum = '27'

# enter path to directory where all input files are located
directname = '/work/levan_lab/mtang/elect_locate/' + 'sub' + subnum
#directname = 'C:\\Users\\siumichael.tang\\Downloads\\elect_locate\\' + 'sub' + subnum

# format filenames of processed mri images, explicit mask, electrode,
filename_wanat_img = '^w3.*\.nii$'  # processed func. images
filename_expmask = 'wEPI_bet_mask\.nii'  # explicit mask
filename_elect = subnum + '_.*Koordinaten.*\.xlsx'  # file containing mni coord. of all electrode pairs

# enter path where ouput struct. is stored at
# fname_op = directname + '\\plots' + '\\visual_artifacts'   # direct. of output matrix
# eafilename_op = 'reho_alff_spikes.mat'   # filename of output file

# enter if output should be written to path (1 = yes, 0 = no)
op_results = 0

# END USER INPUT
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# use get_path function to obtain full path of input files
wanat_file_path = get_path(directname, filename_wanat_img)  # normalized anat. images
expmask_file_path = get_path(directname, filename_expmask)  # normalized mask images
elect_file_path = get_path(directname, filename_elect)  # file containing info. about electrodes coordinates

# load processed images
# specify run index required
run_ind = 0

# create instance of processed image
wanat_inst = nib.load(wanat_file_path[run_ind])

# use get_fdata() method to obtain the actual image
# and use attribute, header, to obtain metadata (dict)
wanat_img = wanat_inst.get_fdata()  # actual image data
wanat_header = wanat_inst.header  # metadata about the image

# create instance of explicit mask, then get exp. mask image data
expmask = nib.load(expmask_file_path[0]).get_fdata()

# load electrode coordinates from .xlsx file into dataframe,
# selected only first 4 columns
elect_df = pd.read_excel(elect_file_path[0], usecols=list(range(5)))

# ---------------------------------------------------------------------------

# Part (II): sort electrodes by their types and obtain their image space
# coordinates

# use sort_elect to sort electrode array by their types
elect_sorted = sort_elect(elect_df)
_, elect_ijk_all = get_elect_contact_ijk(elect_sorted, wanat_header)

# END Part (II): sort electrodes by their types and obtain their image space
# coordinates
# ---------------------------------------------------------------------------

# Part (III): select reference image, on which other images are mapped

# select reference image as first electrode contact,
# manually adjust coordinates to capture entire artifact
ad_x = 1   # manual adjustment in x
x_coor_ref = int(elect_ijk_all[0][-1][0]) - 1 + ad_x
y_coor_ref = int(elect_ijk_all[0][-1][1]) - 1
z_coor_ref = int(elect_ijk_all[0][-1][2]) - 1
spac_ref = 3   # spacing in each direction

# crop out portion enclosing the entire electrode contact
ref_img = np.transpose(wanat_img[x_coor_ref - spac_ref:x_coor_ref + spac_ref + 1:1, \
                               y_coor_ref - spac_ref:y_coor_ref + spac_ref + 1:1, \
                       z_coor_ref - spac_ref:z_coor_ref + spac_ref + 1:1],
                               axes = [1, 0, 2])

# plot ref image to check manual selection
# plt.imshow(np.mean(ref_img, axis=2), cmap='gray', origin='lower')
# plt.imshow(ref_img[:, :, spac_ref], cmap='gray', origin='lower')
# plt.colorbar()
# plt.savefig(os.path.join(fname_op, 'ref_img.eps'), bbox_inches ="tight")

# END Part (III): select reference image, on which other images are mapped
# ---------------------------------------------------------------------------

# Part (IV): select image of every electrode contact

# initialize list, img_sel, to store image selected from processed mri image
img_sel = []

for i in range(len(elect_ijk_all)):
    # for each electrode contact, get image space coordinates, subtract 1 for 0-based indexing
    x_coor = int(elect_ijk_all[i][-1][0]) - 1
    y_coor = int(elect_ijk_all[i][-1][1]) - 1
    z_coor = int(elect_ijk_all[i][-1][2]) - 1
    # specify spacing on each side of electrode contact
    spac = 5
    # on x-y plane
    # crop out patch of image in every cartesian plane, append to img_sel
    img_cropped = np.transpose(wanat_img[x_coor - spac:x_coor + spac + 1:1, \
                               y_coor - spac:y_coor + spac + 1:1, z_coor - spac:z_coor + spac + 1:1],
                               axes = [1, 0, 2])
    img_sel.append(img_cropped)

# get average image without shifting each to align with ref image
avg_img_1 = np.mean(img_sel, axis = 0)
#plt.imshow(np.mean(avg_img_1, axis=2), cmap='gray', origin='lower')

#plt.imshow(np.mean(np.transpose(wanat_img, axes = [1, 0, 2]), axis=2), cmap='gray', origin='lower')
#plt.imshow(np.mean(img_sel[2], axis=2), cmap='gray', origin='lower')
#plt.imshow(np.transpose(wanat_img[:, :, 45]), cmap='gray', origin='lower')
#plt.scatter(x_coor, y_coor, c='r', marker='x')

# END Part (IV): select image of every electrode contact
# ---------------------------------------------------------------------------

# Part (V): shift images to best align on reference image using
# normalized cross correlation, compute average shifted images (elementwise average)

# initialize list to store best-aligned image of each electrode contact
# with reference image
shifted_img = []

# for every image of electrode contact cropped above, use compute_ncc()
# to align the image with reference image, append the aligned image to
# shifted_img
for curr_img in img_sel:
    _, _, _, _, patch_max_ncc = ec_detect.compute_ncc(ref_img, curr_img)
    shifted_img.append(patch_max_ncc)

# compute average shifted images (elementwise average of 3d arrays)
w_1 = np.mean(shifted_img, axis = 0)

# plot shifted image
plt.imshow(np.mean(shifted_img[0], axis=2), cmap='gray', origin='lower')
plt.imshow(np.mean(w_1, axis=2), cmap='gray', origin='lower')
#plt.show()   # show output

# END Part (V): shift images to best align on reference image using
# normalized cross correlation, compute average shifted images (elementwise average
# ---------------------------------------------------------------------------

# Part (VI): get ncc array with single-contact template obtained above

# take transpose of warped anat image
search_img = np.transpose(wanat_img, axes = [1, 0, 2])

# use w_1 as template and obtain ncc array on search image
t1 = time.time()
print(t1)
ncc, _, _, _, _ = ec_detect.compute_ncc(w_1, search_img)
elapsed = time.time() - t1
print(elapsed)

# usually takes around 6 minutes to complete this step

# END Part (VI): get ncc array with single-contact template obtained above
# ---------------------------------------------------------------------------

# Part (VII): run detection algo to get potential points

# set parameters for detection
ncc_thresh = np.max(ncc)*0.75
bbox_spac = 3
iou_thresh = 0.17   # iou_thresh = 0.17 for translating 2 units in each direction when bbox_spac = 3
#iou_thresh = 0.06   # iou_thresh = 0.17 for translating 2 units in each direction when bbox_spac = 3
max_dist_thresh = 6

# run detection algo with parameters entered and display time taken to terminal
t1 = time.time()
bbox_list_3 = run_detect(w_1, ncc, ncc_thresh, bbox_spac, iou_thresh, max_dist_thresh)
elapsed = time.time() - t1
print(elapsed/60)

# save the following variables to path,
# w_1
# bbox_list_3
output_path_w_1 = os.path.join(directname + '/data_py', 'w_1.npy')
output_path_bbox_list_3 = os.path.join(directname + '/data_py', 'bbox_list_3.npy')
np.save(output_path_w_1, w_1, allow_pickle = True)
np.save(output_path_bbox_list_3, bbox_list_3, allow_pickle = True)


# visually compare detection results (green) with marked coordinates (red)
fig7 = plt.figure(7)
plt.imshow(np.transpose(wanat_img[:, :, 45]), cmap='gray', origin='lower')
for item in bbox_list_3:
    ec_coor = item[3]
    plt.scatter(ec_coor[0], ec_coor[1], c='g', marker='.')
for item in elect_ijk_all:
    marked_coor = item[-1]
    plt.scatter(marked_coor[0], marked_coor[1], c='r', marker='.')

# END Part (VII): run detection algo to get potential points
# ---------------------------------------------------------------------------

