import numpy as np
import ec_detect
# ---------------------------------------------------------------------------

# PART (I): step 1 of template matching algo.

# perform step 1 of algo., which contains the following
# -filter out ncc array with translations that give ncc value >= threshold
# -convert translations to indices in image space relative to center of
# image template
def step_1(img_template, ncc_array, ncc_thresh):
    #
    # obtain indices of voxels >= threshold
    # ncc_ind[:3] = indices
    # ncc_ind[-1] = ncc
    ncc_ind = np.argwhere(ncc_array >= ncc_thresh)
    #
    ncc_list_thresholded = []
    for item in ncc_ind:
        ncc_val_req = ncc_array[item[0], item[1], item[2]]
        ncc_list_thresholded.append([item[0], item[1], item[2], ncc_val_req])
    #
    # transpose indices of ncc_ind, add them to centers defined by img_template
    # ecf = electrode contacts found
    # ecf[:3] = indices in image space
    # ecf[-1] = ncc at that voxel
    ecf = []
    for item in ncc_list_thresholded:
        ecf.append([int((img_template.shape[0] - 1) / 2 + item[1]),
                    int((img_template.shape[1] - 1) / 2 + item[0]),
                    int((img_template.shape[2] - 1) / 2 + item[2]), item[-1]])
    #
    return ecf

# ---------------------------------------------------------------------------

# PART(II): step 2 of template matching algo.

# perform step 2 of algo., which contains the following
# -define bounding box for every single-contact detection
# -remove overlapping bounding boxes using non-maximal suppression
def step_2(ecf, bbox_spac, iou_thresh):
    #
    # construct bounding box for every detection of electrode contact
    bbox_list = []
    for item in ecf:
        bbox_para = ec_detect.define_bounding_box(item, bbox_spac)
        bbox_list.append(bbox_para)
    #
    # remove overlapping detections with non-maximum suppression
    # iou_thresh = 0.17 for translating 2 units in each direction,
    # regardless of voxel size
    bbox_list_cleaned = ec_detect.nms(bbox_list, iou_thresh)
    #
    return bbox_list_cleaned

# ---------------------------------------------------------------------------

# Part (III): step 3 of template matching algo.

# perform step 3 of algo., which contains the following
# -remove isolated detections, where there are no detections in
# their vicinity
def step_3(bbox_list_input, max_dist_thresh):
    #
    bbox_list_3 = ec_detect.check_distance(bbox_list_input, max_dist_thresh)
    #
    return bbox_list_3

# ---------------------------------------------------------------------------
