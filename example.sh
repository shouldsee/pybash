echo "### verbose mode, pure bash"
{ echo echo some_cmd; echo echo some_other_cmd; } | tee some_script.sh
pybash < some_script.sh > some_script.sh.log --log-stdout
pybash -c "echo some_cmd; echo some_other_cmd" --single-line --log-stdout

echo "### mixing python and bash"
### assign: python <- bash 
{{some_python_string}} =  ls -1 | head -n3 
### assign: python <- python
{{some_python_list}}   = {{some_python_string.splitlines()}}
### assign: bash   <- python
some_shell_file        = {{ some_python_list[2]}}
### assign: bash   <- bash
some_other_path        = $( realpath $some_shell_file )

### python wihtout assignment
{{import os; import sys;}}
### bash   without assignment
echo "{{sys.version_info}}"

{{url}} = echo "http://example.com"
curl --head {{url}}

### [ToDo]
### - control flow: if statement
### - control flow: for loop 

echo "[done]"


