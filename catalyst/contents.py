
from collections import namedtuple
from subprocess import Popen, PIPE

from support import CatalystError, warn


class ContentsMap(object):
	'''Class to encompass all known commands to list
	the contents of an archive'''


	fields = ['func', 'cmd']


	def __init__(self, defs=None):
		'''Class init

		@param defs: dictionary of Key:[function, cmd]
		'''
		if defs is None:
			defs = {}
		#self.contents = {}
		self.contents_map = {}

		# create the archive type namedtuple classes
		for name in list(defs):
			#obj = self.contents[name] = namedtuple(name, self.fields)
			obj = namedtuple(name, self.fields)
			obj.__slots__ = ()
			self.contents_map[name] = obj._make(defs[name])
		del obj


	def generate_contents(self, file_, getter="auto", verbose=False):
		try:
			archive = getter
			if archive == 'auto' and file_.endswith('.iso'):
				archive = 'isoinfo_l'
			if (archive in ['tar_tv','auto']):
				if file_.endswith('.tgz') or file_.endswith('.tar.gz'):
					archive = 'tar_tvz'
				elif file_.endswith('.tbz2') or file_.endswith('.tar.bz2'):
					archive = 'tar_tvj'
				elif file_.endswith('.tar'):
					archive = 'tar_tv'

			if archive == 'auto':
				warn('File %r has unknown type for automatic detection.'
					% (file_, ))
				return None
			else:
				getter = archive
				func = getattr(self, '_%s_' % self.contents_map[getter].func)
				return func(file_, self.contents_map[getter].cmd, verbose)
		except:
			raise CatalystError(
				"Error generating contents, is appropriate utility " +
				"(%s) installed on your system?"
				% (self.contents_map[getter].cmd), print_traceback=True)


	@staticmethod
	def _calc_contents_(file_, cmd, verbose):
		_cmd = (cmd % {'file': file_ }).split()
		proc = Popen(_cmd, stdout=PIPE, stderr=PIPE)
		results = proc.communicate()
		result = "\n".join(results)
		if verbose:
			print result
		return result

