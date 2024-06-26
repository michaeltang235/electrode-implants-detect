import numpy as np

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

# COMPUTE_NCC(REF_IMG, TARG_IMG):
# inputs:
# REF_IMG = reference image, the template on which target image is matched
# TARG_IMG = target image, on which reference image is translated
# outputs:
# NCC = normalized cross correlation np 3d-array
# MAX_NCC_I, MAX_NCC_J, MAX_NCC_K = indices of max ncc
# PATCH_MAX_NCC = patch (or portion) of target image were max ncc is obtained
# note: REF_IMG is smaller than TARG_IMG, so REF_IMG can translate around
# TARG_IMG to obtain max ncc

def compute_ncc(ref_img, targ_img):

    # obtain dimensions of reference and target images
    ni, nj, nk = ref_img.shape
    nI, nJ, nK = targ_img.shape

    # initialize np array of normalized cross correlation (ncc)
    ncc = np.empty((nI - ni + 1, nJ - nj + 1, nK - nk + 1))

    # translate ref_img around targ_img, obtain patch of targ_img in every
    # translation, and calculate the corresponding ncc
    for i in range(nI - ni + 1):
        for j in range(nJ - nj + 1):
            for k in range(nK - nk + 1):
                patch = targ_img[i:i + (ni - 1) + 1, j:j + (nj - 1) + 1, k:k + (nk - 1) + 1]

                numer = np.sum((ref_img - ref_img.mean()) * (patch - patch.mean()))
                denom = np.sqrt(np.sum((ref_img - ref_img.mean()) ** 2) * np.sum((patch - patch.mean()) ** 2))

                if denom == 0:   # for cases where signal = 0 in voxels near edges of the brain
                    ncc[i, j, k] = 0
                else:
                    ncc[i, j, k] = numer / denom

                #ncc[i, j, k] = np.corrcoef(ref_img.flatten(), patch.flatten())[0, 1]

    # obtain index (in i, j, k) of max ncc in ncc array
    max_ncc_i, max_ncc_j, max_ncc_k = np.unravel_index(ncc.argmax(), ncc.shape)

    # select patch of target image that contains the max ncc with ref image
    patch_max_ncc = targ_img[max_ncc_i:max_ncc_i + (ni - 1) + 1,
                    max_ncc_j:max_ncc_j + (nj - 1) + 1, max_ncc_k:max_ncc_k + (nk - 1) + 1]

    # return required variables
    return ncc, max_ncc_i, max_ncc_j, max_ncc_k, patch_max_ncc


#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

# assume coordinate system as follows:
# x-axis runs from left to right (negative to positive)
# y-axis runs from inside the page to out of the page (negative to positive)
# z-axis runs from bottom to top of page (negative to positive)

# bounding box is defined by 3 vertices and its center:
# 1st vertex = top left corner of face outside of the page
# 2nd vertex = bottom right corner of face outside of the page
# 3rd vertex = bottom right corner of face inside the page
# see page linked below for reference

# ref: https://medium.com/analytics-vidhya/basics-of-bounding-boxes-94e583b5e16c

# DEFINE_BOUNDING_BOX(EC_PARA, BBOX_SPAC):
# inputs:
# EC_PARA = electrode contact parameters, generated by translating
# reference template over target image with normalized cross correlation (ncc)
# computed at each translation
# with format given below
# EC_PARA[:3] = x-, y-, and z-coordinates
# EC_PARA[3] = value of ncc at that detection site
# BBOX_SPAC = bounding box spacing in each direction
# outputs:
# list of 5 elements, with format as follows
# (X1, Y1, Z1) = tuple containing coordinates of 1st vertex
# (X2, Y2, Z2) = tuple containing coordinates of 2nd vertex
# (X3, Y3, Z3) = tuple containing coordinates of 3rd vertex
# (XC, YC, ZC) = tuple containing coordinates of center of bounding box
# NCC_VAL = ncc value of this bounding box (ncc assigned to the center associated)

def define_bounding_box(ec_para, bbox_spac):

    # obtain coordinates of center, convert to int type
    xc = int(ec_para[0])
    yc = int(ec_para[1])
    zc = int(ec_para[2])

    # obtain spacing in each direction, convert to int type
    bbox_spac = int(bbox_spac)

    # construct vertices of bounding box by extending bbox_spac in
    # each direction from center
    x1 = xc - bbox_spac
    y1 = yc + bbox_spac
    z1 = zc + bbox_spac

    x2 = xc + bbox_spac
    y2 = yc + bbox_spac
    z2 = zc - bbox_spac

    x3 = xc + bbox_spac
    y3 = yc - bbox_spac
    z3 = zc - bbox_spac

    # obtain ncc value from input list
    ncc_val = ec_para[-1]

    return [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (xc, yc, zc), ncc_val]


#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

# COMPUTE_IOU(BBOX_1, BBOX_2):
# inputs:
# BBOX_1 = bounding box 1
# BBOX_2 = bounding box 2
# Both are lists of 5 elements made by define_bounding_box(), with format given below
# BBOX_1[:4] = tuples of x-, y-, z-coordinates of vertices and center,
# BBOX_1[4] = ncc value assigned to the box
# outputs:
# IOU =  intersection over union of the two boxes

# for each box,
# width refers to dimension from left to right of page
# height refers to dimension from bottom to top of page
# length refers to dimension from inside to outside of page

# ref:
# https://medium.com/analytics-vidhya/iou-intersection-over-union-705a39e7acef
# https://machinelearningspace.com/intersection-over-union-iou-a-comprehensive-guide/

def compute_iou(bbox_1, bbox_2):

    # obtain coordinates of each of 3 vertices of bounding box 1
    x11, y11, z11 = bbox_1[0]
    x12, y12, z12 = bbox_1[1]
    x13, y13, z13 = bbox_1[2]

    # obtain coordinates of each of 3 vertices of bounding box 2
    x21, y21, z21 = bbox_2[0]
    x22, y22, z22 = bbox_2[1]
    x23, y23, z23 = bbox_2[2]

    # compute x, y, z-coordinates of each vertex of intersection volume
    # see links cited above for details
    x_inter_1 = max(x11, x21)
    y_inter_1 = min(y11, y21)
    z_inter_1 = min(z11, z21)

    x_inter_2 = min(x12, x22)
    y_inter_2 = min(y12, y22)
    z_inter_2 = max(z12, z22)

    x_inter_3 = min(x13, x23)
    y_inter_3 = max(y13, y23)
    z_inter_3 = max(z13, z23)

    # compute width, height, and length of intersection volume
    width_inter = x_inter_2 - x_inter_1
    height_inter = z_inter_1 - z_inter_2
    length_inter = y_inter_2 - y_inter_3

    # in the case of no intersection, negative width, height, and length
    # would be obtained
    # account for false intersection by setting the negative parameter to 0
    if width_inter < 0:
        width_inter = 0

    if height_inter < 0:
        height_inter = 0

    if length_inter < 0:
        length_inter = 0

    # get width, height, and length of each input bounding box
    width_bbox_1 = x12 - x11
    height_bbox_1 = z11 - z12
    length_bbox_1 = y12 - y13

    width_bbox_2 = x22 - x21
    height_bbox_2 = z21 - z22
    length_bbox_2 = y22 - y23

    # compute volume of intersection, bounding boxes 1 and 2
    vol_inter = width_inter * height_inter * length_inter
    vol_bbox_1 = width_bbox_1 * height_bbox_1 * length_bbox_1
    vol_bbox_2 = width_bbox_2 * height_bbox_2 * length_bbox_2

    # compute volume of union
    vol_union = vol_bbox_1 + vol_bbox_2 - vol_inter

    # compute iou
    iou = vol_inter / vol_union

    return iou


#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

# NMS(BBOX_LIST, IOU_THRESH):
# inputs:
# BBOX_LIST = list of bounding boxes, each element contains the follwing
# sublist,
# BBOX_LIST[ith box][:3] = tuple of coordinates of each vertex
# BBOX_LIST[ith box][3] = tuple of coordinates of center of bounding box
# BBOX_LIST[ith box][4] = ncc value assigned to bounding box
# IOU_THRESH = intersection over union (iou) threshold
# outputs:
# BBOX_LIST_NEW = new list of bounding boxes with redundant detections removed

# ref:
# https://medium.com/analytics-vidhya/non-max-suppression-nms-6623e6572536
# https://www.python-engineer.com/posts/remove-elements-in-list-while-iterating/

def nms(bbox_list, iou_thresh):

    # sort bounding box list in descending order of ncc value assigned
    bbox_list_sorted = sorted(bbox_list, key = lambda x: x[-1], reverse = True)

    # create new list to store bounding boxes
    bbox_list_new = []

    # start with the 1st element in the sorted bbox_list,
    # assign the 1st element to the new bbox_list, then
    # loop over every bounding box, compute intersection over union (iou)
    # between the box selected and each other box,
    # if iou between the pair >= threshold (too much overlapping),
    # remove the box from the sorted list
    # if iou between the pair < threshold (not enough over lapping),
    # leave the box in the sorted list as the two boxes being compared
    # are not representing the same object
    while len(bbox_list_sorted) > 0:
        curr_bbox = bbox_list_sorted.pop(0)
        bbox_list_new.append(curr_bbox)

        # here, use bbox_list_sorted[:] to create an instance of a copy of
        # the sorted list at the beginning of the for loop. Then, remove
        # items in the sorted list based on condition. Updated sorted list
        # is then checked at the while statement after. See ref. above for
        # notes on ways to remove items in a for loop without messing up
        # the iteration (how to properly remove items in a for loop)
        for bbox in bbox_list_sorted[:]:
            curr_iou = compute_iou(curr_bbox, bbox)
            if curr_iou >= iou_thresh:
                bbox_list_sorted.remove(bbox)

    return bbox_list_new

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

# if dist btw. any a point and another is <= dist_thresh, the point is considered
# an electrode contact
def check_distance(bbox_list_input, dist_thresh):

    bbox_list_new = []

    for ref_point in bbox_list_input:
        for targ_point in bbox_list_input:
            if ref_point != targ_point:
                ref_point_center = np.array(ref_point[3])
                targ_point_center = np.array(targ_point[3])
                dist = np.linalg.norm(ref_point_center - targ_point_center)
                if dist <= dist_thresh:
                    bbox_list_new.append(ref_point)
                    break

    return bbox_list_new