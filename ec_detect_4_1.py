import numpy as np
import itertools
import ec_detect_3
import ec_detect_4

def get_points_in_search_volume(ref_point_input, bbox_list_input, radius_search_vol):
    #
    ref_point = ref_point_input[:]
    bbox_list = bbox_list_input[:]
    points_within = []
    #
    for item in bbox_list:
        dist = np.linalg.norm(np.array(item[3]) - np.array(ref_point[3]))
        if dist <= radius_search_vol:
            points_within.append(item)
    #
    return ref_point, points_within


def get_targ_list_in_search_volume(ref_point, points_within, eps_collinear, eps_dist, dist_thresh):
    #
    search_list = list(itertools.combinations(points_within, 3))
    comb_matched = []
    bbox_matched = []
    for item in search_list:
        curr_comb = item + (ref_point,)
        counter, _, bbox_comb_sorted = ec_detect_4.check_qualifying_bbox_comb(curr_comb,
                                                                              eps_collinear, eps_dist,
                                                                              dist_thresh)
        if counter == 1:
            comb_matched.append(curr_comb)
            bbox_matched.extend(curr_comb)
            #print('found matched')
            #print('len of comb_matched is ', len(comb_matched))
    #
    targ_list = []
    for item in bbox_matched:
        if item not in targ_list and item != ref_point:
            targ_list.append(item)
    #
    return targ_list

# this version assumes that there is only one set of points in targ_list that could form a qualifying
# combo with ref point. This may not be true when the ref. can form more than one qualifying combo. with
# the points in targ_list.
def check_comb_4(ref_point, targ_list, eps_collinear, eps_dist, dist_thresh, num_contacts_max, num_contacts_min):
    #
    comb_matched = []
    for num_c in range(num_contacts_max - 1, num_contacts_min - 1 - 1, -1):
        search_list = list(itertools.combinations(targ_list, num_c))
        for item in search_list:
            curr_comb = item + (ref_point,)
            #print('form comb of len of ', len(curr_comb))
            counter, _, bbox_comb_sorted = ec_detect_4.check_qualifying_bbox_comb(curr_comb, \
                                                                                  eps_collinear, eps_dist, \
                                                                                  dist_thresh)
            if counter == 1:
                targ_list = ec_detect_4.update_avail_bbox(targ_list, bbox_comb_sorted)
                comb_matched.extend(bbox_comb_sorted)
    #
    return comb_matched

# this version selects the first qualifying combo with the ref. point as output,
# it stops searching for other possible combo. with the ref. once one is identified.
def check_comb_4_1(ref_point, targ_list, eps_collinear, eps_dist, dist_thresh, num_contacts_max, num_contacts_min):
    #
    comb_matched = []
    counter = 0
    for num_c in range(num_contacts_max - 1, num_contacts_min - 1 - 1, -1):
        search_list = list(itertools.combinations(targ_list, num_c))
        for item in search_list:
            curr_comb = item + (ref_point,)
            #print('form comb of len of ', len(curr_comb))
            counter, _, bbox_comb_sorted = ec_detect_4.check_qualifying_bbox_comb(curr_comb, \
                                                                                  eps_collinear, eps_dist, \
                                                                                  dist_thresh)
            if counter == 1:
                comb_matched.extend(bbox_comb_sorted)
                break   # stop searching once a combo with ref point is identified
        if counter == 1:
            break
    #
    return comb_matched


# this version gets all possible combo. with ref point, then select the one with the
# highest avg. ncc as output
def check_comb_4_2(ref_point, targ_list, eps_collinear, eps_dist, dist_thresh, num_contacts_max, num_contacts_min):
    #
    comb_matched = []
    for num_c in range(num_contacts_max - 1, num_contacts_min - 1 - 1, -1):
        # if not targ_list:
        #     break
        search_list = list(itertools.combinations(targ_list, num_c))
        #print('len of search_list = ', len(search_list))
        while search_list:
            item = search_list.pop(0)
            curr_comb = item + (ref_point,)
            counter, _, bbox_comb_sorted = ec_detect_4.check_qualifying_bbox_comb(curr_comb, \
                                                                                  eps_collinear, eps_dist, \
                                                                                  dist_thresh)
            if counter == 1:
                targ_list = ec_detect_4.update_avail_bbox(targ_list, bbox_comb_sorted)
                search_list = list(itertools.combinations(targ_list, num_c))
                comb_matched.append(bbox_comb_sorted)
                #print('found match')
                #print('len of targ_list = ', len(targ_list))
                #print('len of search list = ', len(search_list))
                #print('curr num c = ', num_c)
        #
        #print('no match when num_c = ', num_c)
    #
    #print('len of comb_matched = ', len(comb_matched))
    #
    comb_matched_output = []
    if comb_matched:
        avg_ncc = []
        for comb in comb_matched:
            avg_ncc.append(np.mean([item[-1] for item in comb]))
        ind_req = np.argmax(avg_ncc)
        #print('ind_req = ', ind_req)
        comb_matched_output = comb_matched[ind_req]
    #
    return comb_matched_output


def identify_comb(bbox_list_input, radius_search_vol, eps_collinear, eps_dist, dist_thresh, \
                                     num_contacts_max, num_contacts_min):
    #
    bbox_list = bbox_list_input[:]
    bbox_matched_output = []
    comb_matched_output = []
    round_num = 1
    #
    while len(bbox_list) > 0:
        item = bbox_list.pop(0)
        ref_point, points_within = get_points_in_search_volume(item, bbox_list, radius_search_vol)
        targ_list = get_targ_list_in_search_volume(ref_point, points_within, eps_collinear,
                                                   eps_dist, dist_thresh)
        curr_comb_matched = check_comb_4_2(ref_point, targ_list, eps_collinear, eps_dist, dist_thresh,
                                           num_contacts_max, num_contacts_min)
        #
        if curr_comb_matched:
            comb_matched_output.append(curr_comb_matched)
            bbox_matched_output.extend(curr_comb_matched)
            #print('len of bbox_matched is', len(bbox_matched_output))
            bbox_list = ec_detect_4.update_avail_bbox(bbox_list, bbox_matched_output)
        #print('round_num = ', round_num)
        round_num = round_num + 1
    #
    return comb_matched_output, bbox_matched_output


def check_attachment(bbox_comb_input, bbox_matched_input, pool_bbox, search_radius, eps_collinear, \
                     eps_dist, dist_thresh, num_contacts_max):
    #
    #print('checking current bbox combo')
    curr_bbox_comb = sorted(bbox_comb_input, key=lambda x: x[3])
    #print('len of curr_bbox_comb = ', len(curr_bbox_comb))
    bbox_matched = bbox_matched_input[:]
    #
    counter = 1
    #
    while counter == 1 and len(curr_bbox_comb) < num_contacts_max:
        #
        counter = 0
        #print('begin round')
        #
        first_bbox = curr_bbox_comb[0]  # curr_bbox_comb is already sorted
        last_bbox = curr_bbox_comb[-1]
        #
        avail_bbox = ec_detect_4.update_avail_bbox(pool_bbox, bbox_matched)
        #
        for bbox in avail_bbox:
            #
            dist_to_first_bbox = np.linalg.norm(np.array(bbox[3]) - np.array(first_bbox[3]))
            dist_to_last_bbox = np.linalg.norm(np.array(bbox[3]) - np.array(last_bbox[3]))
            #
            if dist_to_first_bbox <= search_radius or dist_to_last_bbox <= search_radius:
                test_comb = curr_bbox_comb + [bbox]
                counter, _, test_comb = ec_detect_4.check_qualifying_bbox_comb(test_comb, eps_collinear, \
                                                                     eps_dist, dist_thresh)
                if counter == 1:
                    bbox_matched.append(bbox)
                    curr_bbox_comb = test_comb[:]
                    #print('found a match')
                    break   # stop searching, recalculate end points of curr. combo., then
                    # for the remaining of the list of avail bbox
                    #print('statement after break')
        #print('done for this round')
    #
    return curr_bbox_comb, bbox_matched


def check_attachment_all_comb(seg_bbox, bbox_matched_input, pool_bbox, search_radius, \
                              eps_collinear, eps_dist, dist_thresh, num_contacts_max):
    #
    bbox_matched = bbox_matched_input[:]
    #print('bbox_matched = ', len(bbox_matched))
    seg_bbox_output = []
    for seg in seg_bbox:
        #print('searching for current bbox combo')
        curr_bbox_comb, bbox_matched = check_attachment(seg, bbox_matched, pool_bbox, \
                                                        search_radius, eps_collinear, eps_dist, \
                                                        dist_thresh, num_contacts_max)
        seg_bbox_output.append(curr_bbox_comb)
        #print('bbox_matched = ', len(bbox_matched))
        #print('done searching for curr bbox combo')
    #
    return seg_bbox_output, bbox_matched


def count_entries(comb_matched_input):
    #
    count = 0
    for comb in comb_matched_input:
        count = count + len(comb)
    #
    return count