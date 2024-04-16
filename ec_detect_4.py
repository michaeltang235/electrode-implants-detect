import numpy as np
import itertools
import ec_detect_3


def check_collinear(point_a, point_b, point_c, eps):
    #
    vec_b_a = point_b - point_a
    vec_c_a = point_c - point_a
    #
    unit_vec_b_a = vec_b_a / (np.linalg.norm(vec_b_a))
    unit_vec_c_a = vec_c_a / (np.linalg.norm(vec_c_a))
    #
    b = np.dot(unit_vec_b_a, unit_vec_c_a)
    #
    result = 0
    if 1 - eps <= abs(b) <= 1 + eps:
        result = 1
    #
    return result

# def check_set_of_points_collinear(bbox_list, eps_collinear):
#     #
#     center_list = [item[3] for item in bbox_list]
#     #
#     comb_list = list(itertools.combinations(center_list, 3))
#     #
#     counter = 0
#     non_collin_three_points = []
#     for set_of_points in comb_list:
#         point_a = np.array(set_of_points[0])
#         point_b = np.array(set_of_points[1])
#         point_c = np.array(set_of_points[2])
#         counter = check_collinear(point_a, point_b, point_c, eps_collinear)
#         if counter == 0:
#             non_collin_three_points = [point_a, point_b, point_c]
#             #print(point_a, point_b, point_c)
#             break
#     return counter, non_collin_three_points

def check_set_of_points_collinear(bbox_list, eps_collinear):
    #
    comb_list = list(itertools.combinations(bbox_list, 3))
    #
    counter = 0
    non_collin_three_points = []
    for set_of_points in comb_list:
        #
        point_a = set_of_points[0]
        point_b = set_of_points[1]
        point_c = set_of_points[2]
        #
        point_a_center = np.array(point_a[3])
        point_b_center = np.array(point_b[3])
        point_c_center = np.array(point_c[3])
        #
        counter = check_collinear(point_a_center, point_b_center, point_c_center, eps_collinear)
        if counter == 0:
            non_collin_three_points = [point_a, point_b, point_c]
            #print(point_a, point_b, point_c)
            break
    return counter, non_collin_three_points


def check_equidistant(bbox_list, dist_thresh, eps_dist):
    #
    center_list = sorted([item[3] for item in bbox_list])
    #
    counter = 0
    #three_points = []
    for i in range(len(center_list) - 2):
        three_points = center_list[i:i + 3]
        point_a = np.array(three_points[0])
        point_b = np.array(three_points[1])
        point_c = np.array(three_points[2])
        dist_b_a = np.linalg.norm(point_b - point_a)
        dist_c_b = np.linalg.norm(point_c - point_b)
        if (dist_thresh - eps_dist + 0.5 <= dist_b_a <= dist_thresh + eps_dist) \
                and (dist_thresh - eps_dist + 0.5 <= dist_c_b <= dist_thresh + eps_dist):
            counter = 1
        else:
            counter = 0
            three_points = [point_a, point_b, point_c]
            #print(three_points)
            break
    return counter


def check_qualifying_bbox_comb(bbox_comb_input, eps_collinear, eps_dist, dist_thresh):
    #
    bbox_comb_sorted = sorted(bbox_comb_input, key=lambda x: x[3])
    #
    counter, non_col_three_points = check_set_of_points_collinear(bbox_comb_sorted, eps_collinear)
    if counter == 0:
        return counter, non_col_three_points, bbox_comb_sorted
    else:
        counter = check_equidistant(bbox_comb_sorted, dist_thresh, eps_dist)
    #
    return counter, non_col_three_points, bbox_comb_sorted


def update_pool_bbox(w_1, ncc, ncc_thresh_perct):
    #
    ecf = ec_detect_3.step_1(w_1, ncc, np.max(ncc) * ncc_thresh_perct)
    bbox_list_2 = ec_detect_3.step_2(ecf, bbox_spac=3, iou_thresh=0.174)
    bbox_list_3 = ec_detect_3.step_3(bbox_list_2, max_dist_thresh=8)   # original max_dist=6
    #
    return bbox_list_3


def update_avail_bbox(pool_bbox_input, bbox_matched):
    #
    avail_bbox = []
    for item in pool_bbox_input:
        if item not in bbox_matched:
            avail_bbox.append(item)
    #
    return avail_bbox


def check_attachment(bbox_comb_input, bbox_matched_input, pool_bbox, search_radius, eps_collinear, \
                     eps_dist, dist_thresh, num_contacts_max):
    #
    #print('checking current bbox combo')
    curr_bbox_comb = sorted(bbox_comb_input, key=lambda x: x[3])
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
        avail_bbox = update_avail_bbox(pool_bbox, bbox_matched)
        #
        for bbox in avail_bbox:
            #
            dist_to_first_bbox = np.linalg.norm(np.array(bbox[3]) - np.array(first_bbox[3]))
            dist_to_last_bbox = np.linalg.norm(np.array(bbox[3]) - np.array(last_bbox[3]))
            #
            if dist_to_first_bbox <= search_radius or dist_to_last_bbox <= search_radius:
                test_comb = curr_bbox_comb + [bbox]
                counter, _, test_comb = check_qualifying_bbox_comb(test_comb, eps_collinear, \
                                                                     eps_dist, dist_thresh)
                if counter == 1:
                    bbox_matched.append(bbox)
                    curr_bbox_comb = test_comb[:]
                    print('found a match')
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
    print('bbox_matched = ', len(bbox_matched))
    seg_bbox_output = []
    for seg in seg_bbox:
        #print('searching for current bbox combo')
        curr_bbox_comb, bbox_matched = check_attachment(seg, bbox_matched, pool_bbox, \
                                                        search_radius, eps_collinear, eps_dist, \
                                                        dist_thresh, num_contacts_max)
        seg_bbox_output.append(curr_bbox_comb)
        print('bbox_matched = ', len(bbox_matched))
        print('done searching for curr bbox combo')
    #
    return seg_bbox_output, bbox_matched


def update_comb_search_list(comb_search_list_input, non_col_three_points_tot_input):
    #
    comb_search_list = []
    for entry in comb_search_list_input:
        if all(non_col_three_points_tot_input not in entry):
            comb_search_list.append(entry)
    #
    return comb_search_list

#comb_search_list = [entry for entry in comb_search_list_input if non_col_three_points_tot_input not in entry]

def check_combo(pool_bbox, bbox_matched_input, non_col_three_points_tot_input, \
                num_contacts, eps_collinear, eps_dist, dist_thresh):
    #
    bbox_matched = bbox_matched_input[:]
    avail_bbox = update_avail_bbox(pool_bbox, bbox_matched)
    #
    comb_search_list = list(itertools.combinations(avail_bbox, num_contacts))
    #
    if non_col_three_points_tot_input:
        comb_search_list = update_comb_search_list(comb_search_list, non_col_three_points_tot_input)
    #
    non_col_three_points_tot = []
    comb_matched = []
    #
    while len(comb_search_list) > 0:
        curr_comb = comb_search_list.pop(0)
        counter, non_col_three_points, \
            curr_bbox_comb = check_qualifying_bbox_comb(curr_comb, eps_collinear, eps_dist, dist_thresh)
        if non_col_three_points:
            non_col_three_points_tot.append(non_col_three_points)
            comb_search_list = [entry for entry in comb_search_list \
                                if non_col_three_points not in entry]
        else:
            comb_matched.append(curr_bbox_comb)
            bbox_matched.extend(curr_bbox_comb)
    #
    return comb_matched, bbox_matched, non_col_three_points_tot


def check_comb_all(pool_bbox, bbox_matched_input, bbox_comb_matched_input,
                   non_col_three_points_tot_input,
                   eps_collinear, eps_dist, dist_thresh, num_contacts_min, num_contacts_max):
    #
    bbox_matched = bbox_matched_input[:]
    non_col_three_points_tot = non_col_three_points_tot_input[:]
    #
    comb_matched_tot = bbox_comb_matched_input[:]
    #
    for num_c in range(num_contacts_max, num_contacts_min - 1, -1):
        comb_matched, bbox_matched, \
            non_col_three_points_tot = check_combo(pool_bbox, bbox_matched, non_col_three_points_tot,
                                                 num_c, eps_collinear, eps_dist, dist_thresh)
        if comb_matched:
            comb_matched_tot.extend(comb_matched)
    #
    return comb_matched_tot, bbox_matched, non_col_three_points_tot


def matching_algo(bbox_comb_matched, bbox_matched, non_col_three_points_tot, pool_bbox,
                  search_radius, eps_collinear, eps_dist,
                  dist_thresh, num_contacts_min, num_contacts_max, num_elect):
    #
    if bbox_comb_matched:
        bbox_comb_matched, bbox_matched = check_attachment_all_comb(bbox_comb_matched,
                                                                    bbox_matched, pool_bbox,
                                                                    search_radius, eps_collinear,
                                                                    eps_dist, dist_thresh,
                                                                    num_contacts_max)
    #
    if len(bbox_comb_matched) < num_elect:
        bbox_comb_matched, bbox_matched, \
            non_col_three_points_tot = check_comb_all(pool_bbox, bbox_matched, bbox_comb_matched,
                                                                  non_col_three_points_tot,
                                                                  eps_collinear, eps_dist,
                                                                  dist_thresh, num_contacts_min,
                                                                  num_contacts_max)
    #
    return bbox_comb_matched, bbox_matched, non_col_three_points_tot














