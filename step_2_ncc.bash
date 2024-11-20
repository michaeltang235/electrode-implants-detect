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

# get start time 
start_time=$(date +%s)

# assemble path of directory required for each experiment,
# directly call step_2_ncc.py with the paths created as 
# arguments passed and save stdout to file specified for
# that experiment

for exp in ${exp_list[@]}; do
	#
        directname="$(dirname $PWD)/data_py/jul15_2024/$exp"
        w_1_path=$(find "${directname}" -name "w_1*.npy")
	anat_img_path=$(find "$(dirname $PWD)/fsl_resample" -name "re_3*.nii") 
	exp_stdout_path="$PWD/exp_stdout/jul15_2024/${exp}_step_2_ncc.out"
	#
	printf "directname = $directname\n"
	printf "${w_1_path}\n"
	printf "${anat_img_path}\n"
	printf "${exp_stdout_path}\n"
	python -u step_2_ncc.py ${w_1_path} ${anat_img_path} > ${exp_stdout_path}
done
  
# get end time and time elapsed in min.
end_time=$(date +%s)
time_elapsed=$((10**2*($end_time-$start_time)/60))
printf "time elapsed = %.2f min\n" ${time_elapsed}e-2
