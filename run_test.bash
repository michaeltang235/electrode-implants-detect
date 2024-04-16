# enter experiment numbers and series required
exp_num=("1" "2" "3" "4")
series_label="a"

# create and assemble exp_list
exp_list=()
#
for num in ${exp_num[@]}; do
	exp_list+=("exp_${series_label}_$num")
done
#
printf "exp_list = ${exp_list[*]}\n"

# assemble path of directory required for each experiment, 
# directly call test script (test.py) with dir' path created 
# passed as argument and save stdout to file specified for 
# that experiment 
#
for exp in ${exp_list[@]}; do
	directname="$(dirname $PWD)/data_py/ec_detect_script_5_1/$exp"
	printf "directname = $directname\n"
	python run_test.py ${directname} > "./exp_stdout/${exp}.out" 
done	 

#ref:
#https://www.freecodecamp.org/news/bash-array-how-to-declare-an-array-of-strings-in-a-bash-script/
