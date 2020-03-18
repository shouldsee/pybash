[![Build Status](https://travis-ci.com/shouldsee/pybash.svg?branch=master)](https://travis-ci.com/shouldsee/pybash)

# pybash: A hacky Python3 wrapper for bash.

## Requirement: 
	- echo  
	- Python >= 3.5 (python2 backport possible)

## Install:

`pip3 install pybash@https://github.com/shouldsee/pybash/tarball/master --user --upgrade`


## Usage:

```
Version: pybash-0.0.1
Purpose:
	- Mimicing `bash --verbose` on a line-by-line basis. Useful for
	illustrating a bash session. 
	- pybash does not support do-done directives currently
	- runs in verbose mode by default

Options:
	--help     print this help
	--stderr   print stderr to stdout
	-c 

Example:
	pybash -c "echo some_cmd; echo some_other_cmd"

	###---------------
	###-- command
	echo\
	  some_cmd;\
	  echo\
	  some_other_cmd

	###---------------
	###-- stdout
	### some_cmd
	### some_other_cmd
```