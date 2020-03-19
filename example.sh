# alias pybash=./pybash.py
# alias pybash=./pybash.src.py

echo "### verbose mode, pure bash"
{ echo echo some_cmd; echo echo some_other_cmd; } | tee some_script.sh
pybash < some_script.sh > some_script.sh.log --log-stdout
pybash -c "echo some_cmd; echo some_other_cmd" --single-line --log-stdout


echo "### mixing python and bash"
### python wihtout assignment
{{import os; import sys;}}
### bash   without assignment
echo "{{sys.version_info}}"

### python <- bash
{{some_python_string}} =  ls -1 | head -n3 
### python <- python
{{some_python_list}}   = {{some_python_string.splitlines()}}
### bash   <- python
some_shell_file        = {{ some_python_list[2]}}
### bash   <- bash
some_other_path        = $( realpath $some_shell_file )


url     = "http://example.com"
curl --head $url
{{url}} = echo "http://example.com"
curl --head {{url}}

echo "[done]"


