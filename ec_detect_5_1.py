
#---------------------------------
import numpy as np
import itertools
import ec_detect_4
import ec_detect_4_1

#--------------------------------------------------


# sort output avail_bbox by ncc value

def update_avail_bbox(pool_bbox_input, bbox_matched):
    #
    avail_bbox = []
    for item in pool_bbox_input:
        if item not in bbox_matched:
            avail_bbox.append(item)
    #
    # sort avail_bbox by ncc value in descending order
    avail_bbox_op = sorted(avail_bbox, key = lambda x: x[-1], reverse = True)
    #
    return avail_bbox_op

def sort_search_list(search_list_input):
    #
    # compute avg ncc for each comb embedded in search list
    avg_ncc = []
    for comb in search_list_input:
        sum_ncc = 0
        for bbox in comb:
            sum_ncc += bbox[-1]   # ncc is stored in the last entry of bbox nested list
        #
        avg_ncc.append(sum_ncc / len(comb))
    #
    # sort list of avg_ncc in descending order of magnitude
    # ind is a list with each item containing (index, avg ncc) pair
    ind = sorted(enumerate(avg_ncc), key=lambda x: x[1], reverse=True)
    #
    search_list_op = []
    for item in ind:
        ind_req = item[0]   # index is stored in 0th entry in item
        search_list_op.append(search_list_input[ind_req])
    #
    return search_list_op

# this version tries to build comb of length = num_contacts_max-1, then by decreasing the length 1 unit
# until length = num_contacts_min-1. But, this approach will take a long time to complete if there
# are many points within search_vol, as m choose n is large when n is large.
# def build_base_comb(ref_point, points_within, eps_collinear, eps_dist, dist_thresh, num_contacts_max,
#                           radius_search_vol):
#     #
#     num_contacts_min_default = 4  # can be the same as num_contacts_min
#     bbox_comb_op = []
#     curr_bbox_matched = []
#     counter = 0
#     for num_c in range(num_contacts_max - 1, num_contacts_min_default - 1 - 1, -1):
#         # build search list that is sorted by the avg. ncc value of its members
#         #search_list = sort_search_list(list(itertools.combinations(points_within, num_c)))
#         search_list = itertools.combinations(points_within, num_c)
#         for item in search_list:
#             curr_comb = item + (ref_point,)
#             # print('form comb of len of ', len(curr_comb))
#             counter, _, bbox_comb_sorted = ec_detect_4.check_qualifying_bbox_comb(curr_comb, eps_collinear,
#                                                                                   eps_dist, dist_thresh)
#             if counter == 1:
#                 bbox_comb_op.extend(bbox_comb_sorted)
#                 #curr_bbox_matched.extend(bbox_comb_sorted)
#                 print('in build_base_comb: found potential combo')
#                 break  # stop searching once a combo with ref point is identified
#         if counter == 1:
#             break
#     #
#     return bbox_comb_op

# this version of build_base_comb_1 only builds comb. of length equal to 4 from all points within
# search volume. If there are more than 1 base combs built, the one with the highest avg. ncc is
# selected as output
def build_base_comb_1(ref_point, points_within, eps_collinear, eps_dist, dist_thresh, num_contacts_max,
                          radius_search_vol):
    #
    num_contacts_min_default = 4  # can be the same as num_contacts_min
    bbox_comb_list = []   # list storing all comb. that can be formed with ref_point
    bbox_comb_op = []   # output bbox_comb
    counter = 0
    #
    search_list = itertools.combinations(points_within, num_contacts_min_default-1)
    for item in search_list:
        curr_comb = item + (ref_point,)
        counter, _, bbox_comb_sorted = ec_detect_4.check_qualifying_bbox_comb(curr_comb, eps_collinear,
                                                                              eps_dist, dist_thresh)
        if counter == 1:
            bbox_comb_list.append(bbox_comb_sorted)
    #
    if bbox_comb_list:
        #print('in build_base_comb_1: len of bbox_comb_list = ', len(bbox_comb_list))
        avg_ncc = []
        for comb in bbox_comb_list:
            avg_ncc.append(np.mean([item[-1] for item in comb]))
        ind_req = np.argmax(avg_ncc)
        #print('in build_base_comb_1: ind_req = ', ind_req)
        #
        bbox_comb_op = bbox_comb_list[ind_req]
    #
    return bbox_comb_op

# In build_comb, with respect to the input ref_point, a base comb consisting of 4 contacts
# is first built using build_base_comb_1(). Then, additional contacts are added to the
# base comb to form bbox_comb using check_attachment(), until no additional contacts can be added.
# After, the length of the bbox_comb is checked to see if it meets the requirement of number of
# min. contacts. If so, the bbox_comb is added to comb_matched_op array and bbox_matched array
# is updated accordingly. Otherwise, the bbox_comb is assigned to the potential comb array (comb_pot_op)
# ---
# comb_matched_op = comb. matched for the ref point
# bbox_matched_op = bbox matched for the ref point
# comb_pot_op = potential comb. matched for the ref point
# ---
# notes:
# bbox_matched = input bbox_matched array, which is used in check_attachment()
# all output arrays are comb. of bbox w.r.t. ref_point, i.e.
# bbox_matched_op = bbox matched with respect to the ref_point only and
# bbox_matched_op is NOT a subset of bbox_matched

def build_comb(ref_point, avail_bbox, bbox_matched, eps_collinear,
               eps_dist, dist_thresh, num_contacts_max,
               num_contacts_min, radius_search_vol, search_radius):
    #
    # obtain points within search vol. of ref_point
    ref_point, points_within = ec_detect_4_1.get_points_in_search_volume(ref_point, avail_bbox,
                                                                         radius_search_vol)
    #
    # obtain base comb of num. of contacts = 4 for ref_point
    curr_bbox_comb = build_base_comb_1(ref_point, points_within, eps_collinear, eps_dist,
                                      dist_thresh, num_contacts_max, radius_search_vol)
    #
    # if base comb is obtained, look for attachments
    # in check_attachments(), output len(curr_bbox_matched) > input len(curr_bbox_matched), if attachments
    # were added to curr_bbox_comb successfully
    if curr_bbox_comb:
        curr_bbox_matched = bbox_matched + curr_bbox_comb   # update bbox matched for checking attachments
        curr_bbox_comb, curr_bbox_matched = ec_detect_4_1.check_attachment(curr_bbox_comb, curr_bbox_matched,
                                                                           avail_bbox, search_radius, eps_collinear,
                                                                           eps_dist, dist_thresh, num_contacts_max)
    #
    # determine if the curr. bbox comb (curr_bbox_comb) is a comb (that meets the requirement of
    # min. num. of contacts) or a potential comb (comb_pot)
    comb_matched_op = []
    bbox_matched_op = []
    comb_pot_op = []
    if curr_bbox_comb:
        if len(curr_bbox_comb) >= num_contacts_min:
            comb_matched_op.extend(curr_bbox_comb)
            bbox_matched_op.extend(curr_bbox_comb)
            #print('in build_comb: len of bbox_matched_op = ', len(bbox_matched_op))
        else:
            comb_pot_op.extend(curr_bbox_comb)  # not counted in bbox_matched
            #print('found potential comb')
    #
    return comb_matched_op, bbox_matched_op, comb_pot_op

# in identify_comb():
# bbox_matched_output = updated bbox_matched_input, if there are bbox matched
def identify_comb(bbox_list_input, bbox_matched_input, radius_search_vol,
                  eps_collinear, eps_dist, dist_thresh,
                  num_contacts_max, num_contacts_min, search_radius):
    #
    bbox_list = update_avail_bbox(bbox_list_input, bbox_matched_input)  # list of avail. bbox
    bbox_matched_output = bbox_matched_input[:]
    comb_matched_output = []
    pot_comb_output = []
    #
    #print('identify comb, len of bbox_list = ', len(bbox_list))
    #print('identify comb, len of bbox_matched_output = ', len(bbox_matched_output))
    #
    # for each bbox available, call build_comb() to determine if a comb, potential comb, or nothing
    # can be constructed
    while len(bbox_list) > 0:
        ref_point = bbox_list.pop(0)
        curr_comb_matched, curr_bbox_matched, curr_comb_pot = build_comb(ref_point, bbox_list,
                                                                         bbox_matched_output,
                                                                         eps_collinear, eps_dist,
                                                                         dist_thresh, num_contacts_max,
                                                                         num_contacts_min, radius_search_vol,
                                                                         search_radius)
        #
        # outputs of build_comb() (A) are array w.r.t. ref_points only, they are not subsets of bbox_matched_output,
        # comb_matched_output, pot_comb_output (B). Thus, need to add (A) to (B)
        #
        if curr_comb_matched:
            comb_matched_output.append(curr_comb_matched)
            bbox_matched_output.extend(curr_bbox_matched)   # add curr_bbox_matched to array
            print('in identify_comb: len of bbox_matched is', len(bbox_matched_output))
            bbox_list = update_avail_bbox(bbox_list, bbox_matched_output)   # sorted by ncc value
        if curr_comb_pot:
            pot_comb_output.append(curr_comb_pot)
    #
    return comb_matched_output, bbox_matched_output, pot_comb_output


def check_pot_comb(pot_comb_input, bbox_matched_input, pool_bbox,
                   search_radius, eps_collinear, eps_dist, dist_thresh, num_contacts_min, num_contacts_max):
    #
    pot_comb = pot_comb_input[:]
    bbox_matched_1 = bbox_matched_input[:]
    #
    comb_matched_op = []
    bbox_matched_op = []
    comb_pot_op = []
    #
    for curr_pot_comb in pot_comb:
        bbox_matched_i = bbox_matched_1 + curr_pot_comb   # count curr_pot_comb in bbox_matched for this step
        curr_bbox_comb, bbox_matched_2 = ec_detect_4_1.check_attachment(curr_pot_comb, bbox_matched_i,
                                                                      pool_bbox, search_radius, eps_collinear,
                                                                      eps_dist, dist_thresh, num_contacts_max)
        #
        if curr_bbox_comb:
            if len(curr_bbox_comb) >= num_contacts_min:
                comb_matched_op.append(curr_bbox_comb)
                bbox_matched_1 = bbox_matched_2[:]   # update bbox_matched_1 if pot comb is converted to comb
                print('converted pot comb to comb')
            else:
                comb_pot_op.append(curr_bbox_comb)  # not counted in bbox_matched
                print('unable to convert pot to comb')
                # bbox_matched_1 remains the same
    #
    # update bbox_matched_op if bbox_matched_1 was ever updated (there was attachment)
    bbox_matched_op = bbox_matched_1[:]
    #
    return comb_matched_op, bbox_matched_op, comb_pot_op


def matching_algo(w_1, ncc, comb_matched, bbox_matched, comb_pot,
                  ncc_thresh_perct, num_elect_max, radius_search_vol, eps_collinear,
                  eps_dist, dist_thresh, num_contacts_max,
                  num_contacts_min, search_radius):
    #
    while ncc_thresh_perct >= 0.6 and len(comb_matched) < num_elect_max:
        #
        pool_bbox = ec_detect_4.update_pool_bbox(w_1, ncc, ncc_thresh_perct)
        #
        print('--------------------------------')
        print('--------------------------------')
        print('ncc_perct_thresh = ', ncc_thresh_perct)
        #
        # avail bbox is sorted by ncc value
        avail_bbox = update_avail_bbox(pool_bbox, bbox_matched)
        #
        print('len of avail bbox = ', len(avail_bbox))
        #
        print('check attachment:')
        #
        # check for attachment for existing combo
        comb_matched, bbox_matched = ec_detect_4_1.check_attachment_all_comb(comb_matched, bbox_matched, avail_bbox, \
                                                                     search_radius, eps_collinear, eps_dist, \
                                                                     dist_thresh, num_contacts_max)
        print('len of bbox_matched = ', len(bbox_matched))
        print('len of comb matched = ', len(comb_matched))
        nc_found = ec_detect_4_1.count_entries(comb_matched)
        print('num of contacts found = ', nc_found)
        #
        print('check comb pot:')
        # check if potential combo can be converted to combo by looking for attachments
        if comb_pot:
            curr_comb_matched, curr_bbox_matched, curr_comb_pot = check_pot_comb(comb_pot,
                                                                                bbox_matched, pool_bbox,
                                                                                 search_radius, eps_collinear,
                                                                                 eps_dist, dist_thresh,
                                                                                 num_contacts_min, num_contacts_max)
            comb_matched.extend(curr_comb_matched)
            bbox_matched = curr_bbox_matched[:]
            comb_pot = curr_comb_pot[:]
            print('len of bbox_matched = ', len(bbox_matched))
            print('len of comb matched = ', len(comb_matched))
            print('len of pot comb = ', len(comb_pot))
        #
        print('identify comb:')
        # identify combo, if num. elect < num_elect_max
        if len(comb_matched) < num_elect_max:
            curr_comb_matched, curr_bbox_matched, curr_comb_pot = identify_comb(avail_bbox, bbox_matched,
                                                                            radius_search_vol,
                                                                      eps_collinear, eps_dist, dist_thresh,
                                                                      num_contacts_max, num_contacts_min, search_radius)
            bbox_matched = curr_bbox_matched[:]
            comb_matched.extend(curr_comb_matched)
            comb_pot.extend(curr_comb_pot)
            nc_found = ec_detect_4_1.count_entries(comb_matched)
            print('len of bbox_matched = ', len(bbox_matched))
            print('len of comb matched = ', len(comb_matched))
            print('len of pot comb = ', len(comb_pot))
            print('num of contacts found = ', nc_found)
        #
        # comb_matched, bbox_matched = ec_detect_4_1.check_attachment_all_comb(comb_matched, bbox_matched, avail_bbox, \
        #                                                              search_radius, eps_collinear, eps_dist, \
        #                                                              dist_thresh, num_contacts_max)
        # print('len of bbox_matched = ', len(bbox_matched))
        # print('len of comb matched = ', len(comb_matched))
        # nc_found = ec_detect_4_1.count_entries(comb_matched)
        # print('num of contacts found = ', nc_found)
        #
        #curr_comb_matched, bbox_matched, comb_pot_op = check_pot_comb(pot_comb, bbox_matched, pool_bbox, search_radius, eps_collinear, eps_dist, dist_thresh, num_contacts_max)
        #
        ncc_thresh_perct = np.around(ncc_thresh_perct - 0.05, 3)
    #
    return comb_matched, bbox_matched, comb_pot


#----------------------------------------------------------
