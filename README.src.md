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
{{_shell([sys.executable,"./pybash.py","--help"])}}
```

## Contribute/Dev:
  - Edit `pybash.src.py`
  - update version in `setup.py` and in `pybash.src.py`
  - Build with `python3 pybash.src.py --build` if applicable
	- `README.md` 
	- `pybash.py`
