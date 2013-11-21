
import sys
import string
import os
import types
import re
import traceback
import time
from subprocess import Popen


from catalyst.defaults import verbosity, valid_config_file_values

selinux_capable = False
#userpriv_capable = (os.getuid() == 0)
#fakeroot_capable = False

BASH_BINARY             = "/bin/bash"

# set it to 0 for the soft limit, 1 for the hard limit
DESIRED_RLIMIT = 0
try:
	import resource
	max_fd_limit=resource.getrlimit(resource.RLIMIT_NOFILE)[DESIRED_RLIMIT]
except SystemExit, e:
	raise
except:
	# hokay, no resource module.
	max_fd_limit=256

# pids this process knows of.
spawned_pids = []


# a function to turn a string of non-printable characters
# into a string of hex characters
def hexify(str):
	hexStr = string.hexdigits
	r = ''
	for ch in str:
		i = ord(ch)
		r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
	return r


def read_from_clst(file):
	line = ''
	myline = ''
	try:
		myf=open(file,"r")
	except:
		return -1
		#raise CatalystError("Could not open file "+file)
	for line in myf.readlines():
		#line = string.replace(line, "\n", "") # drop newline
		myline = myline + line
	myf.close()
	return myline


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
	def __init__(self, message, print_traceback=False):
		if message:
			if print_traceback:
				(type,value)=sys.exc_info()[:2]
				if value!=None:
					print
					print "Traceback valuse found.  listing..."
					print traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst: "+message
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


def cmd(mycmd, myexc="", env={}, debug=False):
	try:
		sys.stdout.flush()
		args=[BASH_BINARY]
		if "BASH_ENV" not in env:
			env["BASH_ENV"] = "/etc/spork/is/not/valid/profile.env"
		if debug:
			args.append("-x")
		args.append("-c")
		args.append(mycmd)

		if debug:
			print "cmd(); args =", args
		proc = Popen(args, env=env)
		if proc.wait() != 0:
			raise CatalystError("cmd() NON-zero return value from: %s" % myexc,
				print_traceback=False)
	except:
		raise


def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if myfile not in settings:
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
		else:
			if len(settings[myfile])==0:
				raise CatalystError("File variable \"" + myfile +
					"\" has a length of zero (not specified.)", print_traceback=True)
			if settings[myfile][0]=="/":
				if not os.path.exists(settings[myfile]):
					raise CatalystError("Cannot locate specified " + myfile +
						": "+settings[myfile], print_traceback=True)
			elif expand and os.path.exists(os.getcwd()+"/"+settings[myfile]):
				settings[myfile]=os.getcwd()+"/"+settings[myfile]
			else:
				raise CatalystError("Cannot locate specified " + myfile +
					": "+settings[myfile]+" (2nd try)" +
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
					, print_traceback=True)


def parse_makeconf(mylines):
	mymakeconf={}
	pos=0
	pat=re.compile("([0-9a-zA-Z_]*)=(.*)")
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


def read_makeconf(mymakeconffile):
	if os.path.exists(mymakeconffile):
		try:
			try:
				import snakeoil.fileutils
				return snakeoil.fileutils.read_bash_dict(mymakeconffile, sourcing_command="source")
			except ImportError:
				try:
					import portage.util
					return portage.util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
				except:
					try:
						import portage_util
						return portage_util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
					except ImportError:
						myf=open(mymakeconffile,"r")
						mylines=myf.readlines()
						myf.close()
						return parse_makeconf(mylines)
		except:
			raise CatalystError("Could not parse make.conf file " +
				mymakeconffile, print_traceback=True)
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


def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	global valid_config_file_values

	messages = []
	for x in addlargs.keys():
		if x not in validspec and x not in valid_config_file_values and x not in requiredspec:
			messages.append("Argument \""+x+"\" not recognized.")
		else:
			myspec[x]=addlargs[x]

	for x in requiredspec:
		if x not in myspec:
			messages.append("Required argument \""+x+"\" not specified.")

	if messages:
		raise CatalystError('\n\tAlso: '.join(messages))


def touch(myfile):
	try:
		myf=open(myfile,"w")
		myf.close()
	except IOError:
		raise CatalystError("Could not touch "+myfile+".", print_traceback=True)


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
