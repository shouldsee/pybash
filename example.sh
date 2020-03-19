# alias pybash=./pybash.py
{ echo echo some_cmd; echo echo some_other_cmd; } | tee some_script.sh
pybash < some_script.sh > some_script.sh.log
pybash -c "echo some_cmd; echo some_other_cmd" --single-line
pybash -c "echo some_cmd; echo some_other_cmd"
