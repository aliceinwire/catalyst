#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/tinderbox-chroot.sh,v 1.1 2004/04/12 14:39:35 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -n "${clst_ENVSCRIPT}" ]
then
	source /tmp/envscript
	rm -f /tmp/envscript
fi

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps distcc || exit 1
	echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /etc/passwd
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

# START THE BUILD
USE="build" emerge portage
#turn off auto-use:
export USE_ORDER="env:conf:defaults"	
#back up pristine system
rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "/usr/portage/" / /tmp/rsync-bak/ 

for x in ${clst_tinderbox_packages}
do
	emerge --usepkg --buildpkg $x
	if [ "$?" != "0" ]
	then
		echo "! $x" >> /tmp/tinderbox.log	
	else
		echo "$x" >> /tmp/tinderbox.log
	fi
	echo "Syncing from original pristine tinderbox snapshot..."
	rsync -avx --delete --exclude "/root/*" --exclude "/tmp/" --exclude "/usr/portage/*" /tmp/rsync-bak/ /
done