"""
stage2 target, builds upon previous stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import *
from generic_stage_target import *

class stage2_target(generic_stage_target):
	"""
	Builder class for a stage2 installation tarball build.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=["chost"]
		generic_stage_target.__init__(self,spec,addlargs)

	def set_source_path(self):
		if "seedcache" in self.settings["options"] and os.path.isdir(normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/tmp/stage1root/")):
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/tmp/stage1root/")
		else:
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2")
			if os.path.isfile(self.settings["source_path"]):
				if os.path.exists(self.settings["source_path"]):
				# XXX: Is this even necessary if the previous check passes?
					self.settings["source_path_hash"] = \
						self.settings["hash_map"].generate_hash(
							self.settings["source_path"],\
							hash_=self.settings["hash_function"],
							verbose=False)
		print "Source path set to "+self.settings["source_path"]
		if os.path.isdir(self.settings["source_path"]):
			print "\tIf this is not desired, remove this directory or turn of seedcache in the options of catalyst.conf"
			print "\tthe source path will then be "+normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2\n")

	# XXX: How do these override_foo() functions differ from the ones in
	# generic_stage_target and why aren't they in stage3_target?

	def override_chost(self):
		if "chost" in self.settings:
			self.settings["CHOST"]=list_to_string(self.settings["chost"])

	def override_cflags(self):
		if "cflags" in self.settings:
			self.settings["CFLAGS"]=list_to_string(self.settings["cflags"])

	def override_cxxflags(self):
		if "cxxflags" in self.settings:
			self.settings["CXXFLAGS"]=list_to_string(self.settings["cxxflags"])

	def override_ldflags(self):
		if "ldflags" in self.settings:
			self.settings["LDFLAGS"]=list_to_string(self.settings["ldflags"])

	def set_portage_overlay(self):
			generic_stage_target.set_portage_overlay(self)
			if "portage_overlay" in self.settings:
				print "\nWARNING !!!!!"
				print "\tUsing an portage overlay for earlier stages could cause build issues."
				print "\tIf you break it, you buy it. Don't complain to us about it."
				print "\tDont say we did not warn you\n"

def register(foo):
	foo.update({"stage2":stage2_target})
	return foo
