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

# assemble path of directory required for each experiment, 
# directly call test script (run_test.py) with dir' path created 
# passed as argument and save stdout to file specified for 
# that experiment 
#
for exp in ${exp_list[@]}; do
	directname="$(dirname $PWD)/data_py/jul15_2024/$exp"
	printf "directname = $directname\n"
	python run_test_5_1.py ${directname} > "./exp_stdout/jul15_2024/${exp}.out" 
done	 

#ref:
#https://www.freecodecamp.org/news/bash-array-how-to-declare-an-array-of-strings-in-a-bash-script/
