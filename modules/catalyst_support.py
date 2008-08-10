
import sys,string,os,types,re,signal,traceback,time
#import md5,sha
selinux_capable = False
#userpriv_capable = (os.getuid() == 0)
#fakeroot_capable = False
BASH_BINARY             = "/bin/bash"

try:
        import resource
        max_fd_limit=resource.getrlimit(RLIMIT_NOFILE)
except SystemExit, e:
        raise
except:
        # hokay, no resource module.
        max_fd_limit=256

# pids this process knows of.
spawned_pids = []

try:
        import urllib
except SystemExit, e:
        raise

def cleanup(pids,block_exceptions=True):
        """function to go through and reap the list of pids passed to it"""
        global spawned_pids
        if type(pids) == int:
                pids = [pids]
        for x in pids:
                try:
                        os.kill(x,signal.SIGTERM)
                        if os.waitpid(x,os.WNOHANG)[1] == 0:
                                # feisty bugger, still alive.
                                os.kill(x,signal.SIGKILL)
                                os.waitpid(x,0)

                except OSError, oe:
                        if block_exceptions:
                                pass
                        if oe.errno not in (10,3):
                                raise oe
                except SystemExit:
                        raise
                except Exception:
                        if block_exceptions:
                                pass
                try:                    spawned_pids.remove(x)
                except IndexError:      pass



# a function to turn a string of non-printable characters into a string of
# hex characters
def hexify(str):
	hexStr = string.hexdigits
	r = ''
	for ch in str:
		i = ord(ch)
		r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
	return r
# hexify()

def generate_hash(file,hash_function="crc32",verbose=False):
	try:
		return hash_map[hash_function][0](file,hash_map[hash_function][1],hash_map[hash_function][2],\
			hash_map[hash_function][3],verbose)
	except:
		raise CatalystError,"Error generating hash, is appropriate utility installed on your system?"

def calc_hash(file,cmd,cmd_args,id_string="MD5",verbose=False):
	a=os.popen(cmd+" "+cmd_args+" "+file)
	mylines=a.readlines()
	a.close()
	mylines=mylines[0].split()
	result=mylines[0]
	if verbose:
		print id_string+" (%s) = %s" % (file, result)
	return result

def calc_hash2(file,cmd,cmd_args,id_string="MD5",verbose=False):
	a=os.popen(cmd+" "+cmd_args+" "+file)
	header=a.readline()
	mylines=a.readline().split()
	hash=mylines[0]
	short_file=os.path.split(mylines[1])[1]
	a.close()
	result=header+hash+"  "+short_file+"\n"
	if verbose:
		print header+" (%s) = %s" % (short_file, result)
	return result

# This has map must be defined after the function calc_hash
# It is possible to call different functions from this but they must be defined
# before hash_map
# Key,function,cmd,cmd_args,Print string
hash_map={
	 "adler32":[calc_hash2,"shash","-a ADLER32","ADLER32"],\
	 "crc32":[calc_hash2,"shash","-a CRC32","CRC32"],\
	 "crc32b":[calc_hash2,"shash","-a CRC32B","CRC32B"],\
	 "gost":[calc_hash2,"shash","-a GOST","GOST"],\
	 "haval128":[calc_hash2,"shash","-a HAVAL128","HAVAL128"],\
	 "haval160":[calc_hash2,"shash","-a HAVAL160","HAVAL160"],\
	 "haval192":[calc_hash2,"shash","-a HAVAL192","HAVAL192"],\
	 "haval224":[calc_hash2,"shash","-a HAVAL224","HAVAL224"],\
	 "haval256":[calc_hash2,"shash","-a HAVAL256","HAVAL256"],\
	 "md2":[calc_hash2,"shash","-a MD2","MD2"],\
	 "md4":[calc_hash2,"shash","-a MD4","MD4"],\
	 "md5":[calc_hash2,"shash","-a MD5","MD5"],\
	 "ripemd128":[calc_hash2,"shash","-a RIPEMD128","RIPEMD128"],\
	 "ripemd160":[calc_hash2,"shash","-a RIPEMD160","RIPEMD160"],\
	 "ripemd256":[calc_hash2,"shash","-a RIPEMD256","RIPEMD256"],\
	 "ripemd320":[calc_hash2,"shash","-a RIPEMD320","RIPEMD320"],\
	 "sha1":[calc_hash2,"shash","-a SHA1","SHA1"],\
	 "sha224":[calc_hash2,"shash","-a SHA224","SHA224"],\
	 "sha256":[calc_hash2,"shash","-a SHA256","SHA256"],\
	 "sha384":[calc_hash2,"shash","-a SHA384","SHA384"],\
	 "sha512":[calc_hash2,"shash","-a SHA512","SHA512"],\
	 "snefru128":[calc_hash2,"shash","-a SNEFRU128","SNEFRU128"],\
	 "snefru256":[calc_hash2,"shash","-a SNEFRU256","SNEFRU256"],\
	 "tiger":[calc_hash2,"shash","-a TIGER","TIGER"],\
	 "tiger128":[calc_hash2,"shash","-a TIGER128","TIGER128"],\
	 "tiger160":[calc_hash2,"shash","-a TIGER160","TIGER160"],\
	 "whirlpool":[calc_hash2,"shash","-a WHIRLPOOL","WHIRLPOOL"],\
	 }

def read_from_clst(file):
	line = ''
	myline = ''
	try:
		myf=open(file,"r")
	except:
		return -1
		#raise CatalystError, "Could not open file "+file
	for line in myf.readlines():
	    #line = string.replace(line, "\n", "") # drop newline
	    myline = myline + line
	myf.close()
	return myline
# read_from_clst

# these should never be touched
required_build_targets=["generic_target","generic_stage_target"]

# new build types should be added here
valid_build_targets=["stage1_target","stage2_target","stage3_target","stage4_target","grp_target",
			"livecd_stage1_target","livecd_stage2_target","embedded_target",
			"tinderbox_target","snapshot_target","netboot_target","netboot2_target"]

required_config_file_values=["storedir","sharedir","distdir","portdir"]
valid_config_file_values=required_config_file_values[:]
valid_config_file_values.append("PKGCACHE")
valid_config_file_values.append("KERNCACHE")
valid_config_file_values.append("CCACHE")
valid_config_file_values.append("DISTCC")
valid_config_file_values.append("ICECREAM")
valid_config_file_values.append("ENVSCRIPT")
valid_config_file_values.append("AUTORESUME")
valid_config_file_values.append("FETCH")
valid_config_file_values.append("CLEAR_AUTORESUME")
valid_config_file_values.append("options")
valid_config_file_values.append("DEBUG")
valid_config_file_values.append("VERBOSE")
valid_config_file_values.append("PURGE")
valid_config_file_values.append("SNAPCACHE")
valid_config_file_values.append("snapshot_cache")
valid_config_file_values.append("hash_function")
valid_config_file_values.append("digests")
valid_config_file_values.append("SEEDCACHE")

verbosity=1

def list_bashify(mylist):
	if type(mylist)==types.StringType:
		mypack=[mylist]
	else:
		mypack=mylist[:]
	for x in range(0,len(mypack)):
		# surround args with quotes for passing to bash,
		# allows things like "<" to remain intact
		mypack[x]="'"+mypack[x]+"'"
	mypack=string.join(mypack)
	return mypack

def list_to_string(mylist):
	if type(mylist)==types.StringType:
		mypack=[mylist]
	else:
		mypack=mylist[:]
	for x in range(0,len(mypack)):
		# surround args with quotes for passing to bash,
		# allows things like "<" to remain intact
		mypack[x]=mypack[x]
	mypack=string.join(mypack)
	return mypack

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			(type,value)=sys.exc_info()[:2]
			if value!=None:
				print 
				print traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst: "+message
			print
			
class LockInUse(Exception):
	def __init__(self, message):
		if message:
			#(type,value)=sys.exc_info()[:2]
			#if value!=None:
			    #print
			    #kprint traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst lock file in use: "+message
			print

def die(msg=None):
	warn(msg)
	sys.exit(1)

def warn(msg):
	print "!!! catalyst: "+msg


def find_binary(myc):
	"""look through the environmental path for an executable file named whatever myc is"""
        # this sucks. badly.
        p=os.getenv("PATH")
        if p == None:
                return None
        for x in p.split(":"):
                #if it exists, and is executable
                if os.path.exists("%s/%s" % (x,myc)) and os.stat("%s/%s" % (x,myc))[0] & 0x0248:
                        return "%s/%s" % (x,myc)
        return None


def spawn_bash(mycommand,env={},debug=False,opt_name=None,**keywords):
	"""spawn mycommand as an arguement to bash"""
	args=[BASH_BINARY]
	if not opt_name:
	    opt_name=mycommand.split()[0]
	if not env.has_key("BASH_ENV"):
	    env["BASH_ENV"] = "/etc/spork/is/not/valid/profile.env"
	if debug:
	    args.append("-x")
	args.append("-c")
	args.append(mycommand)
	return spawn(args,env=env,opt_name=opt_name,**keywords)

#def spawn_get_output(mycommand,spawn_type=spawn,raw_exit_code=False,emulate_gso=True, \
#        collect_fds=[1],fd_pipes=None,**keywords):
def spawn_get_output(mycommand,raw_exit_code=False,emulate_gso=True, \
        collect_fds=[1],fd_pipes=None,**keywords):
        """call spawn, collecting the output to fd's specified in collect_fds list
        emulate_gso is a compatability hack to emulate commands.getstatusoutput's return, minus the
        requirement it always be a bash call (spawn_type controls the actual spawn call), and minus the
        'lets let log only stdin and let stderr slide by'.

        emulate_gso was deprecated from the day it was added, so convert your code over.
        spawn_type is the passed in function to call- typically spawn_bash, spawn, spawn_sandbox, or spawn_fakeroot"""
        global selinux_capable
        pr,pw=os.pipe()

        #if type(spawn_type) not in [types.FunctionType, types.MethodType]:
        #        s="spawn_type must be passed a function, not",type(spawn_type),spawn_type
        #        raise Exception,s

        if fd_pipes==None:
                fd_pipes={}
                fd_pipes[0] = 0

        for x in collect_fds:
                fd_pipes[x] = pw
        keywords["returnpid"]=True

        mypid=spawn_bash(mycommand,fd_pipes=fd_pipes,**keywords)
        os.close(pw)
        if type(mypid) != types.ListType:
                os.close(pr)
                return [mypid, "%s: No such file or directory" % mycommand.split()[0]]

        fd=os.fdopen(pr,"r")
        mydata=fd.readlines()
        fd.close()
        if emulate_gso:
                mydata=string.join(mydata)
                if len(mydata) and mydata[-1] == "\n":
                        mydata=mydata[:-1]
        retval=os.waitpid(mypid[0],0)[1]
        cleanup(mypid)
        if raw_exit_code:
                return [retval,mydata]
        retval=process_exit_code(retval)
        return [retval, mydata]


# base spawn function
def spawn(mycommand,env={},raw_exit_code=False,opt_name=None,fd_pipes=None,returnpid=False,\
	 uid=None,gid=None,groups=None,umask=None,logfile=None,path_lookup=True,\
	 selinux_context=None, raise_signals=False, func_call=False):
        """base fork/execve function.
	mycommand is the desired command- if you need a command to execute in a bash/sandbox/fakeroot
	environment, use the appropriate spawn call.  This is a straight fork/exec code path.
	Can either have a tuple, or a string passed in.  If uid/gid/groups/umask specified, it changes
	the forked process to said value.  If path_lookup is on, a non-absolute command will be converted
	to an absolute command, otherwise it returns None.
	
	selinux_context is the desired context, dependant on selinux being available.
	opt_name controls the name the processor goes by.
	fd_pipes controls which file descriptor numbers are left open in the forked process- it's a dict of
	current fd's raw fd #, desired #.
	
	func_call is a boolean for specifying to execute a python function- use spawn_func instead.
	raise_signals is questionable.  Basically throw an exception if signal'd.  No exception is thrown
	if raw_input is on.
	
	logfile overloads the specified fd's to write to a tee process which logs to logfile
	returnpid returns the relevant pids (a list, including the logging process if logfile is on).
	
	non-returnpid calls to spawn will block till the process has exited, returning the exitcode/signal
	raw_exit_code controls whether the actual waitpid result is returned, or intrepretted."""


	myc=''
	if not func_call:
		if type(mycommand)==types.StringType:
			mycommand=mycommand.split()
		myc = mycommand[0]
		if not os.access(myc, os.X_OK):
			if not path_lookup:
				return None
			myc = find_binary(myc)
			if myc == None:
			    return None
        mypid=[]
	if logfile:
		pr,pw=os.pipe()
		mypid.extend(spawn(('tee','-i','-a',logfile),returnpid=True,fd_pipes={0:pr,1:1,2:2}))
		retval=os.waitpid(mypid[-1],os.WNOHANG)[1]
		if retval != 0:
			# he's dead jim.
			if raw_exit_code:
				return retval
			return process_exit_code(retval)
		
		if fd_pipes == None:
			fd_pipes={}
			fd_pipes[0] = 0
		fd_pipes[1]=pw
		fd_pipes[2]=pw

	if not opt_name:
		opt_name = mycommand[0]
	myargs=[opt_name]
	myargs.extend(mycommand[1:])
	global spawned_pids
	mypid.append(os.fork())
	if mypid[-1] != 0:
		#log the bugger.
		spawned_pids.extend(mypid)

	if mypid[-1] == 0:
		if func_call:
			spawned_pids = []

		# this may look ugly, but basically it moves file descriptors around to ensure no
		# handles that are needed are accidentally closed during the final dup2 calls.
		trg_fd=[]
		if type(fd_pipes)==types.DictType:
			src_fd=[]
			k=fd_pipes.keys()
			k.sort()

			#build list of which fds will be where, and where they are at currently
			for x in k:
				trg_fd.append(x)
				src_fd.append(fd_pipes[x])
	
			# run through said list dup'ing descriptors so that they won't be waxed
			# by other dup calls.
			for x in range(0,len(trg_fd)):
				if trg_fd[x] == src_fd[x]:
					continue
				if trg_fd[x] in src_fd[x+1:]:
					new=os.dup2(trg_fd[x],max(src_fd) + 1)
					os.close(trg_fd[x])
					try:
						while True:
							src_fd[s.index(trg_fd[x])]=new
					except SystemExit, e:
						raise
					except:
						pass

			# transfer the fds to their final pre-exec position.
			for x in range(0,len(trg_fd)):
				if trg_fd[x] != src_fd[x]:
					os.dup2(src_fd[x], trg_fd[x])
		else:
			trg_fd=[0,1,2]
		
		# wax all open descriptors that weren't requested be left open.
		for x in range(0,max_fd_limit):
			if x not in trg_fd:
				try:
					os.close(x)
                                except SystemExit, e:
                                        raise
                                except:
                                        pass

                # note this order must be preserved- can't change gid/groups if you change uid first.
                if selinux_capable and selinux_context:
                        import selinux
                        selinux.setexec(selinux_context)
                if gid:
                        os.setgid(gid)
                if groups:
                        os.setgroups(groups)
                if uid:
                        os.setuid(uid)
                if umask:
                        os.umask(umask)

                try:
                        #print "execing", myc, myargs
                        if func_call:
                                # either use a passed in func for interpretting the results, or return if no exception.
                                # note the passed in list, and dict are expanded.
                                if len(mycommand) == 4:
                                        os._exit(mycommand[3](mycommand[0](*mycommand[1],**mycommand[2])))
                                try:
                                        mycommand[0](*mycommand[1],**mycommand[2])
                                except Exception,e:
                                        print "caught exception",e," in forked func",mycommand[0]
                                sys.exit(0)

			#os.execvp(myc,myargs)
                        os.execve(myc,myargs,env)
                except SystemExit, e:
                        raise
                except Exception, e:
                        if not func_call:
                                raise str(e)+":\n   "+myc+" "+string.join(myargs)
                        print "func call failed"

                # If the execve fails, we need to report it, and exit
                # *carefully* --- report error here
                os._exit(1)
                sys.exit(1)
                return # should never get reached

        # if we were logging, kill the pipes.
        if logfile:
                os.close(pr)
                os.close(pw)

        if returnpid:
                return mypid

        # loop through pids (typically one, unless logging), either waiting on their death, or waxing them
        # if the main pid (mycommand) returned badly.
        while len(mypid):
                retval=os.waitpid(mypid[-1],0)[1]
                if retval != 0:
                        cleanup(mypid[0:-1],block_exceptions=False)
                        # at this point we've killed all other kid pids generated via this call.
                        # return now.
                        if raw_exit_code:
                                return retval
                        return process_exit_code(retval,throw_signals=raise_signals)
                else:
                        mypid.pop(-1)
        cleanup(mypid)
        return 0

def cmd(mycmd,myexc="",env={}):
	try:
		sys.stdout.flush()
		retval=spawn_bash(mycmd,env)
		if retval != 0:
			raise CatalystError,myexc
	except:
		raise

def process_exit_code(retval,throw_signals=False):
        """process a waitpid returned exit code, returning exit code if it exit'd, or the
        signal if it died from signalling
        if throw_signals is on, it raises a SystemExit if the process was signaled.
        This is intended for usage with threads, although at the moment you can't signal individual
        threads in python, only the master thread, so it's a questionable option."""
        if (retval & 0xff)==0:
                return retval >> 8 # return exit code
        else:
                if throw_signals:
                        #use systemexit, since portage is stupid about exception catching.
                        raise SystemExit()
                return (retval & 0xff) << 8 # interrupted by signal


def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if not settings.has_key(myfile):
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
		else:
		    if len(settings[myfile])==0:
			    raise CatalystError, "File variable \""+myfile+"\" has a length of zero (not specified.)"
		    if settings[myfile][0]=="/":
			    if not os.path.exists(settings[myfile]):
				    raise CatalystError, "Cannot locate specified "+myfile+": "+settings[myfile]
		    elif expand and os.path.exists(os.getcwd()+"/"+settings[myfile]):
			    settings[myfile]=os.getcwd()+"/"+settings[myfile]
		    else:
			    raise CatalystError, "Cannot locate specified "+myfile+": "+settings[myfile]+" (2nd try)"
"""
Spec file format:

The spec file format is a very simple and easy-to-use format for storing data. Here's an example
file:

item1: value1
item2: foo bar oni
item3:
	meep
	bark
	gleep moop
	
This file would be interpreted as defining three items: item1, item2 and item3. item1 would contain
the string value "value1". Item2 would contain an ordered list [ "foo", "bar", "oni" ]. item3
would contain an ordered list as well: [ "meep", "bark", "gleep", "moop" ]. It's important to note
that the order of multiple-value items is preserved, but the order that the items themselves are
defined are not preserved. In other words, "foo", "bar", "oni" ordering is preserved but "item1"
"item2" "item3" ordering is not, as the item strings are stored in a dictionary (hash).
"""

def parse_spec(mylines):
	myspec = {}
	cur_array = []
	trailing_comment=re.compile("#.*$")
	white_space=re.compile("\s+")
	while len(mylines):
		myline = mylines.pop(0).strip()

		# Force the line to be clean 
		# Remove Comments ( anything following # )
		myline = trailing_comment.sub("", myline)

		# Skip any blank lines
		if not myline: continue

		# Look for colon
		msearch = myline.find(':')
		
		# If semicolon found assume its a new key
		# This may cause problems if : are used for key values but works for now
		if msearch != -1:
			# Split on the first semicolon creating two strings in the array mobjs
			mobjs = myline.split(':', 1)
			mobjs[1] = mobjs[1].strip()

			# Check that this key doesn't exist already in the spec
			if myspec.has_key(mobjs[0]):
				raise Exception("You have a duplicate key (" + mobjs[0] + ") in your spec. Please fix it")

			# Start a new array using the first element of mobjs
			cur_array = [mobjs[0]]
			if mobjs[1]:
				# split on white space creating additional array elements
				subarray = white_space.split(mobjs[1])
				if subarray:
					if len(subarray)==1:
						# Store as a string if only one element is found.
						# this is to keep with original catalyst behavior 
						# eventually this may go away if catalyst just works
						# with arrays.
						cur_array.append(subarray[0])
					else:
						cur_array += subarray
		
		# Else add on to the last key we were working on
		else:
			mobjs = white_space.split(myline)
			cur_array += mobjs
		
		# XXX: Do we really still need this "single value is a string" behavior?
		if len(cur_array) == 2:
			myspec[cur_array[0]] = cur_array[1]
		else:
			myspec[cur_array[0]] = cur_array[1:]
	
	for x in myspec.keys():
		# Delete empty key pairs
		if not myspec[x]:
			print "\n\tWARNING: No value set for key " + x + "...deleting"
			del myspec[x]
	return myspec

def parse_makeconf(mylines):
	mymakeconf={}
	pos=0
	pat=re.compile("([a-zA-Z_]*)=(.*)")
	while pos<len(mylines):
		if len(mylines[pos])<=1:
			#skip blanks
			pos += 1
			continue
		if mylines[pos][0] in ["#"," ","\t"]:
			#skip indented lines, comments
			pos += 1
			continue
		else:
			myline=mylines[pos]
			mobj=pat.match(myline)
			pos += 1
			if mobj.group(2):
			    clean_string = re.sub(r"\"",r"",mobj.group(2))
			    mymakeconf[mobj.group(1)]=clean_string
	return mymakeconf

def read_spec(myspecfile):
	try:
		myf=open(myspecfile,"r")
	except:
		raise CatalystError, "Could not open spec file "+myspecfile
	mylines=myf.readlines()
	myf.close()
	return parse_spec(mylines)

def read_makeconf(mymakeconffile):
	if os.path.exists(mymakeconffile):
		try:
			try:
				import snakeoil.fileutils
				return snakeoil.fileutils.read_bash_dict(mymakeconffile, sourcing_command="source")
			except ImportError:
				try:
					import portage_util
					return portage_util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
				except ImportError:
					myf=open(mymakeconffile,"r")
					mylines=myf.readlines()
					myf.close()
					return parse_makeconf(mylines)
		except:
			raise CatalystError, "Could not parse make.conf file "+mymakeconffile
	else:
		makeconf={}
		return makeconf
	
def msg(mymsg,verblevel=1):
	if verbosity>=verblevel:
		print mymsg

def pathcompare(path1,path2):
	# Change double slashes to slash
	path1 = re.sub(r"//",r"/",path1)
	path2 = re.sub(r"//",r"/",path2)
	# Removing ending slash
	path1 = re.sub("/$","",path1)
	path2 = re.sub("/$","",path2)
	
	if path1 == path2:
		return 1
	return 0

def ismount(path):
	"enhanced to handle bind mounts"
	if os.path.ismount(path):
		return 1
	a=os.popen("mount")
	mylines=a.readlines()
	a.close()
	for line in mylines:
		mysplit=line.split()
		if pathcompare(path,mysplit[2]):
			return 1
	return 0

def arg_parse(cmdline):
	#global required_config_file_values
	mydict={}
	for x in cmdline:
		foo=string.split(x,"=",1)
		if len(foo)!=2:
			raise CatalystError, "Invalid arg syntax: "+x

		else:
			mydict[foo[0]]=foo[1]
	
	# if all is well, we should return (we should have bailed before here if not)
	return mydict
		
def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	global valid_config_file_values
	
	for x in addlargs.keys():
		if x not in validspec and x not in valid_config_file_values and x not in requiredspec:
			raise CatalystError, "Argument \""+x+"\" not recognized."
		else:
			myspec[x]=addlargs[x]
	
	for x in requiredspec:
		if not myspec.has_key(x):
			raise CatalystError, "Required argument \""+x+"\" not specified."
	
def spec_dump(myspec):
	for x in myspec.keys():
		print x+": "+repr(myspec[x])

def touch(myfile):
	try:
		myf=open(myfile,"w")
		myf.close()
	except IOError:
		raise CatalystError, "Could not touch "+myfile+"."

def countdown(secs=5, doing="Starting"):
        if secs:
		print ">>> Waiting",secs,"seconds before starting..."
		print ">>> (Control-C to abort)...\n"+doing+" in: ",
		ticks=range(secs)
		ticks.reverse()
		for sec in ticks:
			sys.stdout.write(str(sec+1)+" ")
			sys.stdout.flush()
			time.sleep(1)
		print

def normpath(mypath):
	TrailingSlash=False
        if mypath[-1] == "/":
	    TrailingSlash=True
        newpath = os.path.normpath(mypath)
        if len(newpath) > 1:
                if newpath[:2] == "//":
                        newpath = newpath[1:]
	if TrailingSlash:
	    newpath=newpath+'/'
        return newpath

