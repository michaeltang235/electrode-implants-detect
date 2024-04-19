# this script provides functions for normalization of image template

import numpy as np
import ec_detect

# (I) mean-zero normalization:

def mean_zero_norm(img_input):
    #
    img_subset = img_input[:]
    img_subset_mz = []
    #
    for item in img_subset:
        item_mz = item - item.mean()
        img_subset_mz.append(item_mz)
    #
    return img_subset_mz

# (II) standardization:

def standardization(img_input):
    #
    img_subset = img_input[:]
    img_subset_standard = []
    #
    for item in img_subset:
        item_standard = (item - item.mean()) / item.std()
        img_subset_standard.append(item_standard)
    #
    return img_subset_standard

# (III) min-max normalization:
# in the range of [0, 1]

def min_max_norm(img_input):
    #
    img_subset = img_input[:]
    img_subset_min_max_norm = []
    #
    for item in img_subset:
        item_min_max_norm = (item - item.min()) / (item.max() - item.min())
        img_subset_min_max_norm.append(item_min_max_norm)
    #
    return img_subset_min_max_norm

def select_img(anat_img, elect_ijk_anat, spac):
    #
    img_sel = []
    img_output = []
    #
    for i in range(len(elect_ijk_anat)):
        # for each electrode contact, get image space coordinates, subtract 1 for 0-based indexing
        x_coor = int(elect_ijk_anat[i][0]) - 1
        y_coor = int(elect_ijk_anat[i][1]) - 1
        z_coor = int(elect_ijk_anat[i][2]) - 1
        # specify spacing on each side of electrode contact
        #spac = 5
        # on x-y plane
        # crop out patch of image in every cartesian plane, append to img_sel
        img_cropped = np.transpose(anat_img[x_coor - spac:x_coor + spac + 1:1, \
                                   y_coor - spac:y_coor + spac + 1:1, z_coor - spac:z_coor + spac + 1:1],
                                   axes=[1, 0, 2])
        img_sel.append(img_cropped)
    #
    img_output = img_sel[:]
    #
    return img_output

# def select_img(anat_img, elect_ijk_anat, spac, norm_type):
#     #
#     img_sel = []
#     img_output = []
#     #
#     for i in range(len(elect_ijk_anat)):
#         # for each electrode contact, get image space coordinates, subtract 1 for 0-based indexing
#         x_coor = int(elect_ijk_anat[i][0]) - 1
#         y_coor = int(elect_ijk_anat[i][1]) - 1
#         z_coor = int(elect_ijk_anat[i][2]) - 1
#         # specify spacing on each side of electrode contact
#         #spac = 5
#         # on x-y plane
#         # crop out patch of image in every cartesian plane, append to img_sel
#         img_cropped = np.transpose(anat_img[x_coor - spac:x_coor + spac + 1:1, \
#                                    y_coor - spac:y_coor + spac + 1:1, z_coor - spac:z_coor + spac + 1:1],
#                                    axes=[1, 0, 2])
#         img_sel.append(img_cropped)
#     #
#     img_output = img_sel[:]
#     #
#     # # conduct normalization of img selected based on norm_type input
#     # if norm_type == 2:
#     #     img_output = mean_zero_norm(img_sel)
#     # if norm_type == 3:
#     #     img_output = standardization(img_sel)
#     # if norm_type == 4:
#     #     img_output = min_max_norm(img_sel)
#     # #
#     return img_output


def compute_w_1(ref_img, img_sel, norm_type):
    #
    # initialize list to store best-aligned image of each electrode contact
    # with reference image
    shifted_img = []
    #
    # for every image of electrode contact cropped above, use compute_ncc()
    # to align the image with reference image, append the aligned image to
    # shifted_img
    for curr_img in img_sel:
        _, _, _, _, patch_max_ncc = ec_detect.compute_ncc(ref_img, curr_img)
        shifted_img.append(patch_max_ncc)

    # note: patch_mac_ncc has same dimensions as ref_img, while every
    # item in img_sel is bigger than ref_img, such that the ref_img
    # can be translated on each img_sel to obtain translation with max
    # ncc value
    #
    # conduct normalization of shifted image based on norm_type input
    shifted_img_norm = shifted_img[:]
    if norm_type == 2:
        shifted_img_norm = mean_zero_norm(shifted_img)
    if norm_type == 3:
        shifted_img_norm = standardization(shifted_img)
    if norm_type == 4:
        shifted_img_norm = min_max_norm(shifted_img)
    #
    # compute average normalized shifted images (elementwise average of 3d arrays)
    w_1 = np.mean(shifted_img_norm, axis = 0)
    #
    return w_1

# def compute_w_1(ref_img, img_sel):
#     #
#     # initialize list to store best-aligned image of each electrode contact
#     # with reference image
#     shifted_img = []
#     #
#     # for every image of electrode contact cropped above, use compute_ncc()
#     # to align the image with reference image, append the aligned image to
#     # shifted_img
#     for curr_img in img_sel:
#         _, _, _, _, patch_max_ncc = ec_detect.compute_ncc(ref_img, curr_img)
#         shifted_img.append(patch_max_ncc)
#     #
#     # compute average shifted images (elementwise average of 3d arrays)
#     w_1 = np.mean(shifted_img, axis = 0)
#     #
#     return w_1

import ec_detect_4
import ec_detect_4_1


# -----------------------------------------
def matching_algo(w_1, ncc, comb_matched, bbox_matched,
                  ncc_thresh_perct, num_elect_max, radius_search_vol, eps_collinear,
                  eps_dist, dist_thresh, num_contacts_max,
                  num_contacts_min, search_radius):

    while ncc_thresh_perct >= 0.6 and len(comb_matched) < num_elect_max:
        #
        pool_bbox = ec_detect_4.update_pool_bbox(w_1, ncc, ncc_thresh_perct)
        #
        print('--------------------------------')
        print('--------------------------------')
        print('ncc_perct_thresh = ', ncc_thresh_perct)
        #
        avail_bbox = ec_detect_4.update_avail_bbox(pool_bbox, bbox_matched)
        print('len of avail bbox = ', len(avail_bbox))
        #
        # if len(comb_matched) < num_elect_max:
        curr_comb_matched, curr_bbox_matched = ec_detect_4_1.identify_comb(avail_bbox, radius_search_vol, eps_collinear, \
                                                                           eps_dist, dist_thresh, num_contacts_max, \
                                                                           num_contacts_min)
        bbox_matched.extend(curr_bbox_matched)
        comb_matched.extend(curr_comb_matched)
        nc_found = ec_detect_4_1.count_entries(comb_matched)
        print('len of bbox_matched = ', len(bbox_matched))
        print('len of comb matched = ', len(comb_matched))
        print('num of contacts found = ', nc_found)
        # else:
        #    print('num of elect. reached max limit, not trying to identify comb')
        #
        comb_matched, bbox_matched = ec_detect_4_1.check_attachment_all_comb(comb_matched, bbox_matched, avail_bbox, \
                                                                             search_radius, eps_collinear, eps_dist, \
                                                                             dist_thresh, num_contacts_max)
        print('len of bbox_matched = ', len(bbox_matched))
        print('len of comb matched = ', len(comb_matched))
        nc_found = ec_detect_4_1.count_entries(comb_matched)
        print('num of contacts found = ', nc_found)
        #
        ncc_thresh_perct = np.around(ncc_thresh_perct - 0.05, 3)
    #
    return comb_matched, bbox_matched

# -----------------------------------------



