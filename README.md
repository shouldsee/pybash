[![Build Status](https://travis-ci.com/shouldsee/pybash.svg?branch=master)](https://travis-ci.com/shouldsee/pybash)

# pybash: A hacky Python3 wrapper for bash.

## Requirement: 
	- echo   (dev with: GNU coreutils 8.25)
	- Python >= 3.5 (python2 backport possible)
	- bash (developed with 4.3.48)

## Install:

`pip3 install pybash@https://github.com/shouldsee/pybash/tarball/master --user --upgrade`


## Problems:
	- cannot call pybash within pybash yet.


## Usage:

```

Version: pybash-0.0.5
Purpose:
	- Mimicing `bash --verbose` on a line-by-line basis. Useful for
	illustrating a bash session. 
	- pybash does not support do-done directives currently
	- runs in verbose mode by default

Options:
	--help	      print this help
	--stderr      print stderr to stdout
	-c <cmd> 
	-o <file>     record stdout to <file>
	--add_ts      add timestamp to headers
	--add_dt      add elapsed time to stderr header
	--single-line do not split command by whitespace

Example:
	
	example.sh
		
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
		
		

	example.sh.log
		
		### [pybash-0.0.5]
		### [sys.argv] ./pybash.py --single-line --add-dt --log-stdout
		
		### ---------------
		### [ command]
		echo "### verbose mode, pure bash"
		###
		### [  stdout]
		### ### verbose mode, pure bash
		### ---------------
		
		### ---------------
		### [ command]
		{ echo echo some_cmd; echo echo some_other_cmd; } | tee some_script.sh
		###
		### [  stdout]
		### echo some_cmd
		### echo some_other_cmd
		### ---------------
		
		### ---------------
		### [ command]
		pybash < some_script.sh > some_script.sh.log --log-stdout
		###
		### [  stdout]
		### ---------------
		
		### ---------------
		### [ command]
		pybash -c "echo some_cmd; echo some_other_cmd" --single-line --log-stdout
		###
		### [  stdout]
		### ### [pybash-0.0.5]
		### ### [sys.argv] /home/user/.local/bin/pybash -c echo some_cmd; echo some_other_cmd --single-line --log-stdout
		###
		### ### ---------------
		### ### [ command]
		### echo some_cmd; echo some_other_cmd
		### ###
		### ### [  stdout]
		### ### some_cmd
		### ### some_other_cmd
		### ### ---------------
		### ---------------
		
		### ---------------
		### [ command]
		echo "### mixing python and bash"
		###
		### [  stdout]
		### ### mixing python and bash
		### ---------------
		
		### ---------------
		### [ command]
		{{some_python_string}} =  ls -1 | head -n3
		
		### ---------------
		### [ command]
		{{some_python_list}}   = {{some_python_string.splitlines()}}
		
		### ---------------
		### [ command]
		some_shell_file        = {{ some_python_list[2]}}
		###
		### [  stdout]
		### ---------------
		
		### ---------------
		### [ command]
		some_other_path        = $( realpath $some_shell_file )
		###
		### [  stdout]
		### ---------------
		
		### ---------------
		### [ command]
		{{import os; import sys;}}
		
		### ---------------
		### [ command]
		echo "{{sys.version_info}}"
		###
		### [  stdout]
		### sys.version_info(major=3, minor=5, micro=2, releaselevel='final', serial=0)
		### ---------------
		
		### ---------------
		### [ command]
		{{url}} = echo "http://example.com"
		
		### ---------------
		### [ command]
		curl --head {{url}}
		###
		### [  stdout]
		### HTTP/1.1 200 OK
		### Content-Encoding: gzip
		### Accept-Ranges: bytes
		### Age: 603694
		### Cache-Control: max-age=604800
		### Content-Type: text/html; charset=UTF-8
		### Date: Thu, 19 Mar 2020 14:49:09 GMT
		### Etag: "3147526947"
		### Expires: Thu, 26 Mar 2020 14:49:09 GMT
		### Last-Modified: Thu, 17 Oct 2019 07:18:26 GMT
		### Server: ECS (sjc/4E71)
		### X-Cache: HIT
		### Content-Length: 648
		###
		### ---------------
		
		### ---------------
		### [ command]
		echo "[done]"
		###
		### [  stdout]
		### [done]
		### ---------------
}




```

## Contribute/Dev:
  - Edit `pybash.src.py`
  - update version in `setup.py` and in `pybash.src.py`
  - Build with `python3 pybash.src.py --build` if applicable
	- `README.md` 
	- `pybash.py`