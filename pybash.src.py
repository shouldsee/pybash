#!/usr/bin/env python3
__doc__ ='''
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
		{% for line in open("example.sh","r") %}
		{{line.rstrip()}}{% endfor %}

	example.sh.log
		{% for line in _shell('set -x; python3 ./pybash.py <example.sh --single-line --add-dt --log-stdout | tee example.sh.log',shell=True).splitlines() %}
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

# @staticmethod
def silent(s):
	return ''

import importlib
class _ns(object):
	_shell = lambda *a,**kw:subprocess.check_output(*a,**kw).decode('utf8')
	_silent = lambda *a,**kw: ''
	hash = hash
	repr = repr
	import sys,os,io;
	def _import(name):
		for _name in name.split():
			setattr(ns, _name, importlib.import_module(_name))

	# _import = lambda name: setattr(ns, name, importlib.import_module(name))
	_assign = lambda x,y: setattr()

from pprint import pprint
import builtins
ns = _ns()
ns.__dict__.update(_ns.__dict__)
ns.__dict__.update(builtins.__dict__)
# ns._import = lambda name: setattr(ns, name, importlib.import_module(name))

# ns_dict = dict(ns.__dict__)
# [setattr(ns, k, v) for k,v in builtins.__dict__.items()]

def _main(args, fd, writer):
	extra_args={}
	extra_args.setdefault('add_ts',0)
	extra_args.setdefault('add_dt',0)
	extra_args.setdefault('single_line',0)
	extra_args.setdefault('log_mode','')

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

	if 1:
		# writing = {'stdout','command','stderr'}
		writing = {'stdout','command',}
	else:
		writing = set()

	if '--stderr' in args:
		args.remove('--stderr')
		writing.add('stderr')
	if '--log-stdout' in args:
		i = args.index('--log-stdout')
		extra_args['log_mode'] = '/dev/stdout'
		# args[i+1]
		del args[i:i+1]
		# args.remove('--log')
		# extra_args['log_mode'] = 1

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
def rstrip(s,suffix):
	if s.endswith(suffix):
		s = s[:-len(suffix)]
	return s

def _main_proc(fd, writer, writing, bash_args, extra_args):
	# extra_args['add_dt'] =1
	timestamp   = extra_args['add_ts']
	add_dt      = extra_args['add_dt']
	single_line = extra_args['single_line']
	log_mode    = extra_args['log_mode']
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
	p = subprocess.Popen(cmd, 
		# stdin = None,
		# stdin = io.open(),
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
	last = [time.time()]
	for line in it:
		k = 'command'
		_writer = {1:writer,0:lambda *x:None}[k in writing]
		write_header(_writer, k,timestamp,add_dt,writing) if log_mode else None
		if log_mode and k in writing:	
			if single_line:
				### [fragile] keep indentation?
				writer(line.lstrip().rstrip() +'\n')
			else:
				writer('\\\n  '.join(line.strip().split())+'\n')


		sig = ".pybash_done"
		def has_bracket(lhs):
			return lhs[:2] == '{'*2 and lhs[-2:] == '}'*2
		def is_jinja_assign(line):
			lhs = None
			rhs = None
			sp = line.split('=',1)

			if len(sp) != 2:
				lhs = sp[0].strip()
				if has_bracket(lhs):
					return 3,lhs[2:-2].strip(),None
				else:
					return 0,lhs,None
			lhs, rhs = sp[0].strip(),sp[1].strip()
			has_bracket_lhs = has_bracket(lhs)
			has_bracket_rhs = has_bracket(rhs)
			if has_bracket(lhs) and not has_bracket(rhs):
				## python <- bash
				lhs = lhs[2:-2]
				return 1,lhs,rhs
			elif has_bracket(lhs) and has_bracket(rhs):
				return 2,lhs[2:-2],rhs[2:-2]
			elif not has_bracket_lhs and not has_bracket_rhs:
				return 0, lhs.strip()+'='+ rhs.strip(), None
			elif not has_bracket_lhs and has_bracket_rhs:
				return 0, lhs.strip()+'=' + rhs.strip(), None
		suc, lhs, rhs = is_jinja_assign(line)
		print('#[suc]',suc,lhs,rhs) if debug else None
		if suc == 2:
			exec("%s=%s"%(lhs,rhs),ns.__dict__)
		elif suc==3:
			exec("%s"%lhs, ns.__dict__)
			# assert 0
			# exec(lhs, (ns.__dict__))
		elif suc==1:
			print('#[jinja2_format]%s'%	repr(line)) if debug else None
			_stdout = []
			_stderr = []
			p.stdin.write(('%s\n'%rhs+'echo %s\n echo %s >&2\n'%(sig,sig)).encode())

			def get_type(lhs):
				sp = lhs.split(':')
				if len(sp) ==2:
					typ,lhs= sp
					typ = eval(typ.strip(),ns.__dict__)
				elif len(sp)==1:
					lhs = sp[0]
					typ = str
				return typ,lhs

			cls, lhs = get_type(lhs)
			# print('[cls]',cls,lhs)

			for k, fh, wts in [
				('stdout',p.stdout,{1:_stdout.append}),
				('stderr',p.stderr,{1:_stderr.append}),
				]:
				_writer = wts[1]
				while True:
					retcode = p.poll()
					if retcode is not None:
						_writer('### exit %s\n'%retcode)
						return (retcode)
					oline = fh.readline().decode() 
					if oline[:-1].endswith(sig):
						oline = rstrip(oline[:-1],sig)
						_writer(oline)
						break
					else:
						_writer( oline )

			if cls in [int,float]:
				assert len(_stdout)==1, _stdout
				_stdout = cls(_stdout[0])

			elif cls in [str,bytes]:
				if cls == bytes:
					raise NotImplemented 
				_stdout = cls(''.join(_stdout))
			elif cls in [tuple,list]:
				_stdout = cls(_stdout)
			else:
				assert 0,"Not defined for type: %s"%cls

			exec('ns.%s= _stdout'%lhs)
		else:
			line = lhs
			line = jinja2_format( line, **ns.__dict__).rstrip()	+'\n'
			p.stdin.write((line+'echo %s\n echo %s >&2\n'%(sig,sig)).encode())
			# print(repr(line)) if debug else None
			
			for k,fh,wts in [
				('stdout',p.stdout,
					{1:writer, 0:lambda x:None}), 
				('stderr',p.stderr,
					{1:writer, 0:lambda x:None})
			]:
				_writer = wts[k in writing]
				write_header(_writer, k,timestamp,add_dt,writing) if log_mode else None
				while True:
					retcode = p.poll()
					if retcode is not None:
						(_writer if log_mode else sys.stderr.write)('### exit %s\n'%retcode)
						return (retcode)
					oline = fh.readline().decode() 
					# oline = jinja2_format( oline, **ns_dict).rstrip()	+'\n'

					if oline[:-1].endswith(sig):
						oline = rstrip(oline[:-1],sig)
						if log_mode:
							_writer('### %s\n'%oline) if oline else None
							_writer('### %s\n'%('-'*15)) 
						else:
							getattr( sys, k ).write( "%s" % oline )
						# (_writer if log_mode else [].append)('### %s\n'%oline) if oline else None
						# _writer('### %s\n'%oline) if oline else None
						break
					else: 
						##### normal output stream
						if log_mode:
							_writer('### %s'%oline)
						else:
							getattr( sys, k ).write(oline)
						# (_writer if log_mode else [].append)('### %s'%oline)
	return 0


import builtins
from jinja2 import Template, StrictUndefined
def jinja2_format(s,**context):
	# d = builtins.__dict__.copy()
	# d = ns_dict.copy()
	d = {}
	d.update(context)
	return Template(s,undefined=StrictUndefined).render(**d)

import shutil
from pprint import pprint
def build_main():
	# _shell = lambda *a,**kw:subprocess.check_output(*a,**kw).decode('utf8')
	# import os,shutil,sys;
	# _shell('./pybash.py <example.sh  --single-line --add-dt  >example.sh.log',shell=True)
	shutil.copy2('pybash.src.py','pybash.py')
	with open('pybash.src.py','r') as f:
		template = f.read()
		out = jinja2_format(template,**ns.__dict__)
		with open('pybash.py','w') as fo:
			fo.write(out)

	with open('README.src.md','r') as f:
		with open('README.md','w') as fo:
			template = f.read()
			out = jinja2_format(template,**ns.__dict__)
			fo.write(out)

debug  =0


if __name__ == '__main__':
	if '--build' in sys.argv:
		build_main()
		sys.exit(0)
	main()

