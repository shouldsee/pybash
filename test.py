import unittest2
from path import Path
from pprint import pprint

import os,sys
import subprocess

import importlib
from pybash import _main,version
class Case(unittest2.TestCase):
	def test_c(self):
		buf = []
		_main(['pybash.src.py','-c','"echo aaa;echo bbb"'], None, writer=buf.append)
		buf = ''.join(buf).splitlines()[2:]
		exp= \
['### [pybash-%s]'%version,
 '### [sys.argv] test.py',
 '',
 '### ---------------',
 '### [ command]',
 'echo\\',
 '  aaa;echo\\',
 '  bbb',
 '### ',
 '### [  stdout]',
 '### aaa',
 '### bbb',
 '### ---------------'][2:]
 # ,pprint(buf)
		assert buf == exp,(pprint(buf),pprint(exp),print(repr(version)))

		pprint(buf)
	def test_pipe(self):
		# buf = []
		buf = subprocess.check_output(' '.join(['echo "echo aaa;echo bbb"|',sys.executable,'pybash.src.py']),shell=1)
		buf = buf.decode().splitlines()
		exp = \
[
 '### [pybash-%s]'%version,
 '### [sys.argv] pybash.src.py',
 '',
 '### ---------------',
 '### [ command]',
 'echo\\',
 '  aaa;echo\\',
 '  bbb',
 '### ',
 '### [  stdout]',
 '### aaa',
 '### bbb',
 '### ---------------']
		assert buf == exp,(pprint(buf),pprint(exp),print(repr(version)))

import pdb
import traceback
def debugTestRunner(post_mortem=None):
	"""unittest runner doing post mortem debugging on failing tests"""
	if post_mortem is None:
		post_mortem = pdb.post_mortem
	class DebugTestResult(unittest2.TextTestResult):
		def addError(self, test, err):
			# called before tearDown()
			traceback.print_exception(*err)
			post_mortem(err[2])
			super(DebugTestResult, self).addError(test, err)
		def addFailure(self, test, err):
			traceback.print_exception(*err)
			post_mortem(err[2])
			super(DebugTestResult, self).addFailure(test, err)
	return unittest2.TextTestRunner(resultclass=DebugTestResult)

if __name__ == '__main__':
	# print('[testing]%s'%__file__)
	if '--all' in sys.argv:
		del sys.argv[sys.argv.index('--all')]
		
	if '--pdb' in sys.argv:
		del sys.argv[sys.argv.index('--pdb')]
		unittest2.main(testRunner=debugTestRunner())
	else:
		unittest2.main(testRunner=None)