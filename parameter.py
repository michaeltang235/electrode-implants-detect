#------------------------------------------------
# list of parameters
eps_collinear = 0.04
eps_dist = 2.5   # original = 1.5
dist_thresh = 5
search_radius = 7   # original = 7
num_contacts_min = 4
num_contacts_max = 8

ncc_thresh_perct = 0.75
ncc_thresh_perct_min = 0.5
ncc_thresh_perct_decre = 0.05

radius_search_vol = 5*4
num_elect_max = 9

# enter path of w_1 and ncc, as well as that of output variables, comb_matched, bbox_matched
directname = '/work/levan_lab/mtang/elect_locate/sub27/data_py/ec_detect_script_5_1/exp_a_1/'
w_1_filename = 'w_1.npy'
ncc_filename = 'ncc.npy'
comb_matched_filename = 'comb_matched.npy'
bbox_matched_filename = 'bbox_matched.npy'

w_1_path = directname + w_1_filename
ncc_path = directname + ncc_filename
comb_matched_path = directname + comb_matched_filename
bbox_matched_path = directname + bbox_matched_filename
print('done loading parameters')