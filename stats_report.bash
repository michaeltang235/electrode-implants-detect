# This script calls stats_report.py which compares detected 
# electrodes (comb_matched) with those in the dataset (.xlsx)
# for every experiment defined in exp_list (see below for details)  

# enter experiment numbers and series required
exp_num=("1" "2" "3" "4")
series_label="b"

# create and assemble exp_list
exp_list=()
#
for num in ${exp_num[@]}; do
        exp_list+=("exp_${series_label}_$num")
done
#
printf "exp_list = ${exp_list[*]}\n"

# assemble path of files required for each experiment, 
# call stats_report.py with the paths assembled as input
# arguments passed and save output (.txt) to output path
# specified within stats_report.py

# input arguments required when calling stats_report.py
# 1st arg. = path of electrode coordinates .xlsx file
# 2nd arg. = path of file containing electrode coordinates in anatomical space
# 3rd arg. = path of comb_matched array

directname=$(dirname $PWD)
elect_excel_file=$(find "${directname}" -name "*Koordinaten.xlsx")
elect_coord_anat_file="${directname}/fsl_resample/elect_contacts_coord_anat.txt"

printf "$directname \n"
printf "$elect_excel_file \n"
printf "$elect_coord_anat_file \n"

for exp in ${exp_list[@]}; do 
	comb_matched_file="${directname}/data_py/jul15_2024/${exp}/comb_matched.npy"
	printf "$comb_matched_file \n"
	python stats_report.py ${elect_excel_file} ${elect_coord_anat_file} ${comb_matched_file} 
done


