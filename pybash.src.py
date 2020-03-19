#!/usr/bin/env python3
__doc__ ='''
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
	{% for line in _shell('python3 ./pybash.py <example.sh  --single-line --add-dt  | tee example.sh.log ',shell=True).splitlines() %}
	{{[line.rstrip(),print(line)][0]}}{%endfor%}
}
'''
version = __doc__.lstrip().split('\n',1)[0].split('-')[-1].strip()
import itertools
import os, stat, sys
import io
import subprocess
import time

import time
import datetime
import tzlocal
# import tzlocal
def date_formatIso(obj=None):
	if obj is None:
		obj = datetime.datetime.utcnow()
	local_tz = tzlocal.get_localzone() 
	s  = obj.replace(microsecond=0,tzinfo=local_tz).isoformat()
	return s


class Unbuffered(object):
	'''S ource:https://stackoverflow.com/a/107717/8083313
	'''
	def __init__(self, stream):
		self.stream = stream
	def write(self, data):
		self.stream.write(data)
		self.stream.flush()
	def writelines(self, datas):
		self.stream.writelines(datas)
		self.stream.flush()
	def __getattr__(self, attr):
		return getattr(self.stream, attr)
sys.stdout=Unbuffered(sys.stdout)
sys.stderr=Unbuffered(sys.stderr)

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
		print('[1]'	,repr(line)) if debug else None
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
	if '--version' in sys.argv:
		print('pybash-%s'%version)
		sys.exit(0)
	sys.exit(_main(None,None,None))

def _help(exit):
	print(__doc__)
	sys.exit(exit)

def _stderr(s):
	sys.stderr.write(str(s))
def _main(args, fd, writer):
	extra_args={}
	extra_args.setdefault('add_ts',0)
	extra_args.setdefault('add_dt',0)
	extra_args.setdefault('single_line',0)

	# _stderr(repr(sys.stdout)+'\n')
	# sys.exit(0)
	# assert 0
	closes = []
	if writer is None:
		def writer(s):
			sys.stdout.write(s)

	if args is None:
		args = sys.argv[:]
		# args = [x for x in sys.argv]

	if '-o' in args: 
		i = args.index('-o')
		fo = open(args[i+1],'w')
		del args[i:i+2]
		old_writer = writer
		def writer(s):
			old_writer(s)
			fo.write(s)
		closes.append(fo.close)

	if '--help' in args:
		_help(0)
	if '--add-ts' in args:
		extra_args['add_ts']=1
		args.remove('--add-ts')
	if '--add-dt' in args:
		extra_args['add_dt']=1
		args.remove('--add-dt')
	if '--single-line' in args:
		extra_args['single_line']=1
		args.remove('--single-line')

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
		# print()


	if fd is None:
		if len(script):
			args.remove(script[0])
			fd = open(script[0],'r').readline
			if '-e' not in args:
				args.append('-e')

		else:
			fd = sys.stdin.readline
	bash_args = args[1:]
	writer('### [pybash-%s]\n'%version)
	writer('### [sys.argv] %s\n'%(' '.join(sys.argv)))
	retcode = _main_proc(fd, writer, writing, bash_args,extra_args)
	[x() for x in closes]
	return retcode

def _main_proc(fd, writer, writing, bash_args, extra_args):
	# extra_args['add_dt'] =1
	timestamp = extra_args['add_ts']
	add_dt = extra_args['add_dt']
	single_line=extra_args['single_line']
	def write_header(_writer,k,timestamp, add_dt, writing):

		# if k in writing:
		if k == 'command':
			_writer('\n')
			_writer('### %s\n'%('-'*15)) 
		else:
			_writer('### \n')
		# kb = ('[%8s]'%k)
		_writer('### [%8s]'%(k,))
		if timestamp:
			_writer('[time_iso:%s][%.2f]'%(date_formatIso(),time.time()))
		if add_dt:
			if k =='stderr':
				curr = time.time()
				_writer('\n### [elapsed:%.3f s]'%(curr-last[0]))
				last[0]=curr
		_writer('\n')
	# else:
	# 		None
		# return '%s[%s][%.2f]'%(date_formatIso(),time.time())
		# [%s][%.2f]
	it = parser(fd)
	cmd =  ['bash']+ bash_args
	p = subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
	last = [time.time()]

	for line in it:
		k = 'command'
		_writer = writer
		write_header(_writer, k,timestamp,add_dt,writing)
		# writer(  '###-- %s\n'%k) if k in writing else None
		if k in writing:	
			# writer('[line]%s'%repr(line))
			if single_line:
				### [fragile] keep indentation?
				writer(line.lstrip().rstrip() +'\n')
			else:
				writer('\\\n  '.join(line.strip().split())+'\n')
		# writer(  line) if k in writing else None
		# continue 
		sig = ".pybash_done"
		p.stdin.write((line+'echo %s\n echo %s >&2\n'%(sig,sig)).encode())
		# print(repr(p.returncode))
		# retcode = p.poll()
		# print(('[aaaa]',retcode))
			# assert 0
		for k,fh in [('stdout',p.stdout), ('stderr',p.stderr)]:
			if k =='stderr':
				if k in writing:
					_writer = writer
				else:
					_writer = sys.stderr.write
			else:
				if k in writing:
					_writer = writer
				else:
					_writer = lambda x:None

			write_header(_writer, k,timestamp,add_dt,writing)
			while True:
				retcode = p.poll()
				if retcode is not None:
					_writer('### exit %s\n'%retcode)
					return (retcode)
				oline = fh.readline().decode() 
				if oline[:-1]==sig:
					_writer(  '### %s\n'%('-'*15)) 
					break
				else:
					_writer('### %s'%oline)
	return 0



from jinja2 import Template, StrictUndefined
def jinja2_format(s,**context):
	# d = context.copy()
	d = __builtins__.__dict__.copy()
	d.update(context)
	return Template(s,undefined=StrictUndefined).render(**d)

import shutil
from pprint import pprint
def build_main():
	_shell = lambda *a,**kw:subprocess.check_output(*a,**kw).decode('utf8')
	import os,shutil,sys;
	# _shell('./pybash.py <example.sh  --single-line --add-dt  >example.sh.log',shell=True)
	with open('pybash.src.py','r') as f:
		shutil.copy2('pybash.src.py','pybash.py')
		template = f.read()
		out = jinja2_format(template,**locals())
		with open('pybash.py','w') as fo:
			# pprint(template.splitlines())
			# pprint(out.splitlines())
			fo.write(out)

	with open('README.src.md','r') as f:
		with open('README.md','w') as fo:
			fo.write(jinja2_format(f.read(),**locals()))


if __name__ == '__main__':
	if '--build' in sys.argv:
		build_main()
		sys.exit(0)
	main()
