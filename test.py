import unittest2
from path import Path
from pprint import pprint

import os,sys
import subprocess

from pybash import _main,version
class Case(unittest2.TestCase):
	def test_c(self):
		buf = []
		_main(['pybash.src.py','-c','"echo aaa;echo bbb"'], None, writer=buf.append)
		buf = ''.join(buf).splitlines()	
		assert buf == \
['### [pybash-%s]'%version,
 '### [sys.argv] test.py',
 '### ---------------',
 '### [ command]',
 'echo\\',
 '  aaa;echo\\',
 '  bbb',
 '### ',
 '### [  stdout]',
 '### aaa',
 '### bbb',
 '### ---------------'],pprint(buf)

		pprint(buf)
	def test_pipe(self):
		# buf = []
		buf = subprocess.check_output(' '.join(['echo "echo aaa;echo bbb"|',sys.executable,'pybash.src.py']),shell=1)
		buf = buf.decode().splitlines()
		assert buf[1:] == [
		'### [pybash-]',
 '### [sys.argv] pybash.src.py',
 '### ---------------',
 '### [ command]',
 'echo\\',
 '  aaa;echo\\',
 '  bbb',
 '### ',
 '### [  stdout]',
 '### aaa',
 '### bbb',
 '### ---------------'][1:],pprint(buf)

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