#!/usr/bin/python

# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>
# Copyright 2013 Brian Dolbec <dolsen@gentoo.org>

'''resume.py

Performs autoresume tracking file operations such as
set, unset, is_set, is_unset, enabled, clear_all
'''

import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE
import traceback

from catalyst.fileops import ensure_dirs, pjoin, listdir_files
from catalyst.support import touch


class AutoResumeError(Exception):
	def __init__(self, message, print_traceback=False):
		if message:
			if print_traceback:
				(type,value)=sys.exc_info()[:2]
				if value!=None:
					print
					print "Traceback values found.  listing..."
					print traceback.print_exc(file=sys.stdout)
			print "!!! catalyst: AutoResumeError " + message
			print


class AutoResume(object):
	'''Class for tracking and handling all aspects of
	the autoresume option and related files.
	'''


	def __init__(self, basedir, mode=0755):
		self.basedir = basedir
		ensure_dirs(basedir, mode=mode, fatal=True)
		self._points = {}
		self._init_points_()


	def _init_points_(self):
		'''Internal function which reads the autoresume directory and
		for existing autoresume points and adds them to our _points variable
		'''
		existing = listdir_files(self.basedir, False)
		for point in existing:
			self._points[point] = pjoin(self.basedir, point)


	def enable(self, point, data=None):
		'''Sets the resume point 'ON'

		@param point: string.  name of the resume point to enable
		@param data: string of information to store, or None
		@return boolean
		'''
		if point in self._points and not data:
			return True
		fname = pjoin(self.basedir, point)
		if data:
			with open(fname,"w") as myf:
				myf.write(data)
		else:
			try:
				touch(fname)
				self._points[point] = fname
			except Exception as e:
				print AutoResumeError(str(e))
				return False
		return True


	def get(self, point, no_lf=True):
		'''Gets any data stored inside a resume point

		@param point: string.  name of the resume point to enable
		@return data: string of information stored, or None
		'''
		if point in self._points:
			try:
				with open(self._points[point], 'r') as myf:
					data = myf.read()
				if data and no_lf:
					data = data.replace('\n', '')
			except OSError as e:
				print AutoResumeError(str(e))
				return None
			return data
		return None


	def disable(self, point):
		'''Sets the resume point 'OFF'

		@param point: string.  name of the resume point to disable
		@return boolean
		'''
		if point not in self._points:
			return True
		try:
			os.unlink(self._points[point])
			self._points.pop(point)
		except Exception as e:
			print AutoResumeError(str(e))
			return False
		return True


	def is_enabled(self, point):
		'''Returns True if the resume point 'ON'

		@param point: string.  name of the resume point enabled
		@return boolean
		'''
		return point in self._points


	def is_disabled(self, point):
		'''Returns True if the resume point 'OFF'

		@param point: string.  name of the resume point not enabled
		@return boolean
		'''
		return point not in self._points


	@property
	def enabled(self):
		'''Returns a list of enabled points
		'''
		return list(self._points)


	def clear_all(self):
		'''Clear all active resume points

		@return boolean
		'''
		try:
			print "Emptying directory---", self.basedir
			"""
			stat the dir, delete the dir, recreate the dir and set
			the proper perms and ownership
			"""
			mystat=os.stat(self.basedir)
			if os.uname()[0] == "FreeBSD":
				cmd("chflags -R noschg " + self.basedir,\
					"Could not remove immutable flag for file "\
					+ self.basedir)
			shutil.rmtree(self.basedir)
			ensure_dirs(self.basedir, 0755)
			os.chown(self.basedir,mystat[ST_UID],mystat[ST_GID])
			os.chmod(self.basedir,mystat[ST_MODE])
			self._points = {}
		except Exception as e:
			print AutoResumeError(str(e))
			return False
		return True
