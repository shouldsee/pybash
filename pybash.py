#!/usr/bin/env python3
__doc__ ='''
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
   
'''
import itertools
import os, stat, sys
import io
import subprocess
import time
class ParsingError(Exception):
	pass
def parser(_readline, debug=0):
	'''
	Parse lines from a generator
	'''

	buf = []
	def _yield():
		res = ''.join(buf)
		del buf[:]
		return res
	while True:
		line = _readline()
		# line = it.readline()
		# .decode()
		print('1'	,repr(line)) if debug else None
		if line == '':
			if len(buf):
				raise ParsingError('Unexpected EOF: %r'%buf)
			# yield ['exit 0\n']
			break
		elif line.strip().startswith('#'):
			if len(buf):
				raise ParsingError('Unexpected EOF: %r'%buf)
			else:
				continue
		elif line.endswith('\\\n'):
			buf.append(line[:-2])
		elif line.endswith('\n'):
			if not line.strip():
				continue
			buf.append(line)
			yield _yield()
		else:
			assert 0,repr(line)


def main():
	_main(None,None,None)

def _help(exit):
	print(__doc__)
	sys.exit(exit)

def _main(args, fd, writer):

	if writer is None:
		def writer(s):
			sys.stdout.write(s)
	if args is None:
		args = sys.argv

	if '--help' in args:
		_help(0)

	writing = ['stdout','command']
	if '--stderr' in args:
		args.remove('--stderr')
		writing.append('stderr')

	script = [x for x in args[1:] if not x.startswith('-')]
	assert len(script)<=1,(script,)

	if "-c" in args:
		i = args.index('-c')
		cmd = args[i+1].strip('"\'')+'\n' ##### [fragile] potentially allowing broken command?
		fd = iter([cmd,'']).__next__
		del args[i:i+2]

	if fd is None:
		if len(script):
			args.remove(script[0])
			fd = open(script[0],'r').readline
		else:
			fd = sys.stdin.readline
	bash_args = args[1:]
	_main_proc(fd, writer, writing, bash_args)

def _main_proc(fd, writer, writing, bash_args):
	it = parser(fd)
	cmd =  ['bash']+ bash_args
	p = subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
	for line in it:
		k = 'command'
		writer(  '\n###%s\n'%('-'*15)) 
		writer(  '###-- %s\n'%k) if k in writing else None
		if k in writing:	
			writer('\\\n  '.join(line.split())+'\n')

		# writer(  line) if k in writing else None
		# continue 
		sig = ".vbash_done"
		p.stdin.write((line+'echo %s\n echo %s >&2\n'%(sig,sig)).encode())
		for k,fh in [('stdout',p.stdout), ('stderr',p.stderr)]:
			writer(  '\n###%s\n'%('-'*15)) if k in writing else None
			writer('###-- %s\n'%k) if k in writing else None
			while True:
				oline = fh.readline().decode()
				if oline[:-1]==sig:
					break
				else:
					# if fh is p.stdout:
					writer('### %s'%oline) if k in writing else None

	return 

if __name__ == '__main__':
	main()
	# None,None,None)

