# generic netboot image specfile
# used to build a network bootable image

# The subarch can be any of the supported catalyst subarches (like athlon-xp).
# Refer to the catalyst reference manual for suppurted subarches.
# http://www.gentoo.org/proj/en/releng/catalyst/reference.xml
# example:
# subarch: athlon-xp
subarch:

# The version stamp is an identifier for the build.  It can be anything you wish# it to be, but it is usually a date.
# example:
# version_stamp: 2005.0
version_stamp:

# The target specifies what target we want catalyst to do.  For building a
# netboot image, we use the netboot target.
# example:
# target: netboot
target:

# The rel_type defines what kind of build we are doing.  This is merely another
# identifier, but it useful for allowing multiple concurrent builds.  Usually,
# default will suffice.
# example:
# rel_type: default
rel_type:

# This is the system profile to be used by catalyst to build this target.  It is# specified as a relative path from /usr/portage/profiles.
# example:
# profile: default-linux/x86/2005.0
profile:

# This specifies which snapshot to use for building this target.
# example:
# snapshot: 20050324
snapshot:

# This specifies where the seed stage comes from for this target,  The path is
# relative to $clst_sharedir/builds.  The rel_type is also used as a path prefix# for the seed.
# example:
# default/stage3-x86-2004.3
source_subpath:

# These are the hosts used as distcc slaves when distcc is enabled in your
# catalyst.conf.  It follows the same syntax as distcc-config --set-hosts and
# is entirely optional.
# example:
# distcc_hosts: 127.0.0.1 192.168.0.1
distcc_hosts:

# This is an optional directory containing portage configuration files.  It
# follows the same syntax as /etc/portage and should be consistent across all
# targets to minimize problems.
# example:
# portage_confdir: /etc/portage
portage_confdir:

# This option tells catalyst which kernel sources to merge for building this
# image.  This can use normal portage atoms to specify a specific version.
# example:
# netboot/kernel/sources: gentoo-sources
netboot/kernel/sources:

# This option is the full path and filename to a kernel .config file that is
# used by genkernel to compile the kernel for this image.
# example:
# netboot/kernel/config: /tmp/2.6.11-netboot.config
netboot/kernel/config:

# This option sets the USE flags used to build the kernel.  These USE flags are
# additive from the default USE for the specified profile.
# example:
# netboot/kernel/use: ultra1
netboot/kernel/use:

# This option sets the USE flags with which the optional packages below are
# built.  Like the kernel USE, they are additive.
# example:
# netboot/use:
netboot/use:

# The netboot target builds busybox for its root filesystem.  This option is
# where you specify the full path and filename to your busybox configuration.
# example
# netboot/busybox_config: /tmp/busybox.config
netboot/busybox_config:

# This is the full path and filename to the tarball to use as the base for the
# netboot image.
# example:
# netboot/base_tarball: /usr/lib/catalyst/netboot/netboot-base.tar.bz2
netboot/base_tarball:

# These are the packages that will be built for your netboot image using the USE
# flags set in netboot/use.  These package names are also labels used later when
# determining what files to copy into your netboot image.
# example:
# netboot/packages: raidtools xfsprogs e2fsprogs reiserfsprogs

# This is where you tell catalyst which files from each package to copy into the
# netboot image.
# example:
# netboot/packages/raidtools/files: /sbin/raidstart /sbin/mkraid /sbin/detect_multipath /sbin/raidreconf /sbin/raidstop /sbin/raidhotadd /sbin/raidhotremove /sbin/raidsetfaulty /sbin/raid0run
netboot/packages/raidtools/files:

# Here is the same thing for xfsprogs.
# example:
# netboot/packages/xfsprogs/files: /sbin/mkfs.xfs /sbin/xfs_repair /bin/xfs_check
netboot/packages/xfsprogs/files:

# Here is the same thing for e2fsprogs.
# example:
# netboot/packages/e2fsprogs/files: /sbin/mke2fs
netboot/packages/e2fsprogs/files:

# Here is the same thing for reiserfsprogs.
# example:
# netboot/packages/reiserfsprogs/files: /sbin/mkreiserfs
netboot/packages/reiserfsprogs/files:

# This is a list of any other files, not belonging to the above packages, that
# you would wish to have copied into your netboot image.
# example:
# netboot/extra_files: /lib/libresolv.so.2 /lib/libnss_compat.so.2 /lib/libnss_dns.so.2 /lib/libnss_files.so.2 /sbin/consoletype
netboot/extra_files:
