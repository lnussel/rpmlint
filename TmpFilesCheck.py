# -*- coding: utf-8 -*-
#############################################################################
# File          : TmpFilesCheck.py
# Package       : rpmlint
# Author        : Ludwig Nussel
# Created on    : Wed Sep 03 10:36 2014
# Purpose       : Check systemd created tmpfiles are included in filelist
#############################################################################

import os
import re

from Filter import addDetails, printError, printWarning
import AbstractCheck
import Pkg
import stat

class TmpFilesCheck(AbstractCheck.AbstractCheck):
    '''Check systemd created tmpfiles are included in filelist'''

    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(self, "TmpFilesCheck")
        self._spec_file = None

    def check(self, pkg):
        if pkg.isSource():
            return

        # see tmpfiles.d(5)
        interesting_types = ('f', 'F', 'w', 'd', 'D', 'p', 'L', 'c', 'b')

        for fn, pkgfile in pkg.files().items():
            if not fn.startswith('/usr/lib/tmpfiles.d/'):
                continue
            if not stat.S_ISREG(pkgfile.mode):
                printWarning(pkg, "tmpfile-not-regular-file", fn)
                continue
            for line in open(pkgfile.path):
                # skip comments
                line = line.split('#')[0].split('\n')[0]
                line = line.lstrip()
                if not len(line):
                    continue
                line = re.split(r'\s+', line)
                # format is
                #Type Path        Mode UID  GID  Age Argument
                # we only need type and path
                if len(line) < 3:
                    continue
                t = line[0]
                p = line[1]
                if t.endswith('!'):
                    t = t[:-1]
                if not t in interesting_types:
                    continue

                if not p in pkg.files():
                    printWarning(pkg, "tmpfile-not-in-filelist", p)
                    continue
                if not pkg.files()[p].is_ghost:
                    printWarning(pkg, "tmpfile-not-ghost", p)

check = TmpFilesCheck()

addDetails(
'tmpfile-not-regular-file',
'''files in tmpfiles.d need to be regular files''', # otherwise we won't open it :-)
'tmpfile-not-in-filelist',
'''please add the specified file to your %files section as %ghost so
users can easily query who created the file, it gets uninstalled on
package removal and finally other rpmlint checks see it''',
'tmpfile-not-ghost',
'''the specified file is not marked as %ghost although created at
runtime via tmpfiles mechanism.'''
)
# vim: sw=4 et
