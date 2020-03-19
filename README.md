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

Version: pybash-0.0.4
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
	
	### [pybash-0.0.4]
	### [sys.argv] ./pybash.py --single-line --add-dt
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
	pybash < some_script.sh > some_script.sh.log
	###
	### [  stdout]
	### ---------------
	
	### ---------------
	### [ command]
	pybash -c "echo some_cmd; echo some_other_cmd" --single-line
	###
	### [  stdout]
	### ### [pybash-0.0.3]
	### ### [sys.argv] /home/user/.local/bin/pybash -c echo some_cmd; echo some_other_cmd --single-line
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
	pybash -c "echo some_cmd; echo some_other_cmd"
	###
	### [  stdout]
	### ### [pybash-0.0.3]
	### ### [sys.argv] /home/user/.local/bin/pybash -c echo some_cmd; echo some_other_cmd
	### ### ---------------
	### ### [ command]
	### echo	###   some_cmd;	###   echo	###   some_other_cmd###
	### ### [  stdout]
	### ### some_cmd
	### ### some_other_cmd
	### ### ---------------
	### ---------------
}


```

## Contribute/Dev:
  - Edit `pybash.src.py`
  - update version in `setup.py` and in `pybash.src.py`
  - Build with `python3 pybash.src.py --build` if applicable
	- `README.md` 
	- `pybash.py`