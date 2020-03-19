#!/usr/bin/env python3
__doc__ ='''
Version: pybash-0.0.3
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

	### [pybash-0.0.2]
	### ./pybash.py --single-line --add-dt
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
	### ### [pybash-0.0.2]
	### ### /home/user/.local/bin/pybash -c echo some_cmd; echo some_other_cmd --single-line
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
	### ### /home/user/.local/bin/pybash -c echo some_cmd; echo some_other_cmd
	### ### [pybash-0.0.2]
	### ### ---------------
	### ### [ command]
	### echo\
	###   some_cmd;\
	###   echo\
	###   some_other_cmd### 
	### ### [  stdout]
	### ### some_cmd
	### ### some_other_cmd
	### ### ---------------
	### ---------------
   
'''
version = __doc__.lstrip().split('\n',1)[0].split('-')[-1].strip()
import itertools
import os, stat, sys
import io
import subprocess
import time

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
	writer('### [sys.argv] %s'%(' '.join(sys.argv)))
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
			_writer(  '### %s\n'%('-'*15)) 
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
		# else:
		# 	writer('###-- %s'%(kb,))
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
			if single_line:
				### [fragile] keep indentation?
				writer(line.lstrip())
			else:
				writer('\\\n  '.join(line.split()))
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

import time
import datetime
import tzlocal
import sys
import collections, functools
import os
_this_mod = sys.modules[__name__]
_DICT_CLASS = collections.OrderedDict

# import pymisca.header
import decorator

# import tzlocal
def date_formatIso(obj=None):
	if obj is None:
		obj = datetime.datetime.utcnow()
	local_tz = tzlocal.get_localzone() 
	s  = obj.replace(microsecond=0,tzinfo=local_tz).isoformat()
	return s

import json
class scope__timer(object):	
	def __init__(self,data = None, key = None, OFNAME = None, show=0):
		if data is None:
			data = collections.OrderedDict()
		self.data = data
		self.key = key
		self.show = show
		self.OFNAME = os.path.abspath(OFNAME) if OFNAME else OFNAME
#		 if OUTNAME is not None
#		 self.f=open(OUTNAME,"w")
		return 
	
	def __enter__(self):
		assert key is not None
		# key = self.key = self.key or pymisca.header.get__frameName(level=1)
		self.data.setdefault(key, collections.OrderedDict())
		self.d = self.data[key]
		
#		 sys.modules["__main__"]
		self.start = datetime.datetime.now()

		return self

	def __exit__(self, *args):
		self.end = datetime.datetime.now()
		self.dt = self.end - self.start
		d = self.d
		d['start'] =_this_mod.date__formatIso(getattr(self,"start"))
		d['end'] = _this_mod.date__formatIso(getattr(self,"end"))
		d['dt'] = float(getattr(self,"dt").total_seconds())
		if self.OFNAME is not None:
			if pymisca.shell.file__notEmpty(self.OFNAME):
				data = pymisca.shell.read__json( self.OFNAME )
				data.update(self.data)
			else:
				data = self.data
				
			with open(self.OFNAME, "w") as f:
				json.dump(data, f, indent=4)
		if self.show:
			print(json.dumps(d,indent=4))
#				 f.close()

ScopeTimer = scope__timer
# timer = func__timer

def func__timer(timeDict,key=None, debug=0):
	def dec(f,key=key):
		if key is None:
			key = f.__name__
			
#		 @decorator.decorator
		@functools.wraps(f)			
		def wrap(*args, **kw):
#			 ts = time.time()
			ts = datetime.datetime.now()
			
			result = f(*args, **kw)
#			 te = time.time()
			te = datetime.datetime.now()
	
			timeDict[key] = d = _DICT_CLASS()
			d['start'] =_this_mod.date__formatIso(ts)
			d['end'] = _this_mod.date__formatIso(te)
			d['dt'] = float((te - ts).total_seconds())
			
			if debug:
				print(d)
#			 print 'func:%r args:[%r, %r] took: %2.4f sec' % \
#			   (f.__name__, args, kw, te-ts)
			return result
		return wrap
	return dec
timer = func__timer


if __name__ == '__main__':
	main()
	# None,None,None)

