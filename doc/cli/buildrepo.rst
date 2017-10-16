=========
buildrepo
=========

----------------------------------------------
Tool for managing repository with metro builds
----------------------------------------------

:Author: Daniel Robbins <drobbins@funtoo.org>
:Date:   2017-09-27
:Copyright: Funtoo Technologies, LLC
:Version: 2.0.0
:Manual section: 8
:Manual group: funtoo

SYNOPSIS
========

  :program:`buildrepo` [*clean*] [*nextbuild*] [*empties*] [*fails*] [*index.xml*] [*zap*] [*cmd*] [*digestgen*]

DESCRIPTION
===========

The :program:`buildrepo` command can do various metro repository manipulations including but not limited to
listing failed builds, telling the buildbot script which architecture/subarchitecture
should be build next, and last but not least generating digests of the stage archives.


OPTIONS
=======
.. program:: buildrepo

.. option:: clean

  Lists old portage snapshots and old builds, or stale builds that got interrupted or failed.
  The command generates shell commands that can be piped into shell. So the command itself doesn't
  delete anything.

.. option:: nextbuild

  List variables for the buildbot.sh script about the next build that needs to be run.

.. option:: empties

  TODO: Description for empties

.. option:: fails

  Lists all builds with their failed count as the first column.

.. option:: index.xml

  Generates index.xml inside Metro's mirror path with information about the repository.

.. option:: zap

  Clear failed count on all builds.

.. option:: cmd

  TODO: Description for cmd

.. option:: digestgen

  This creates digests (sha256) and signs the build if gpg is set for the user running metro.

A config file for the repository is needed to be able to use :program:`buildrepo`.
Currently :program:`buildrepo` searches for this file in this location /root/.buildbot.

FILES
========

~/.buildbot
  This is the default configuration file for :program:`buildrepo` and buildbot.sh scripts. It is used
  to define which flavor/arch/subarch should be build on this build-server, but also
  the builds rotation/retention policy and failure handling.

EXAMPLES
========
List all local failures of builds::

  $ buildrepo fails
  0   2017-10-01 /home/mirror/funtoo/funtoo-current/x86-64bit/generic_64
  0   2017-10-02 /home/mirror/funtoo/funtoo-current/x86-64bit/intel64-westmere
  0         None /home/mirror/funtoo/funtoo-current/x86-64bit/amd64-k8
  0   2017-10-01 /home/mirror/funtoo/funtoo-current/pure64/generic_64-pure64
  0   2017-10-01 /home/mirror/funtoo/funtoo-current/pure64/intel64-westmere-pure64
  0   2017-10-01 /home/mirror/funtoo/funtoo-current/pure64/amd64-k8-pure64

Show information about next scheduled build::

  $ buildrepo nextbuild
  build=funtoo-current
  arch_desc=x86-64bit
  subarch=amd64-k8
  fulldate=None
  nextdate=2017-10-02
  failcount=0
  target=full
  extras=''

SEE ALSO
========

   :manpage:`buildbot.sh(8)`

BUGS
====

Metro bugs are managed at Funtoo Bug Tracker `Bugs : Metro <https://bugs.funtoo.org>`__
