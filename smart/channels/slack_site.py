#
# Copyright (c) 2004 Conectiva, Inc.
#
# Written by Gustavo Niemeyer <niemeyer@conectiva.com>
#
# This file is part of Smart Package Manager.
#
# Smart Package Manager is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# Smart Package Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Smart Package Manager; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from smart.backends.slack.loader import SlackSiteLoader
from smart.util.filetools import getFileDigest
from smart.channel import PackageChannel
from smart.const import SUCCEEDED, FAILED, NEVER
from smart import *
import posixpath

class SlackSiteChannel(PackageChannel):

    def __init__(self, baseurl, compressed, *args):
        super(SlackSiteChannel, self).__init__(*args)
        self._baseurl = baseurl
        self._compressed = compressed

    def getCacheCompareURLs(self):
        return [posixpath.join(self._baseurl, "PACKAGES.TXT")]

    def getFetchSteps(self):
        return 2

    def fetch(self, fetcher, progress):

        fetcher.reset()

        if self._compressed:
            PACKAGES_TXT="PACKAGES.TXT.gz"
            CHECKSUMS_md5="CHECKSUMS.md5.gz"
        else:
            PACKAGES_TXT="PACKAGES.TXT"
            CHECKSUMS_md5="CHECKSUMS.md5"

        # Fetch packages file
        url = posixpath.join(self._baseurl, PACKAGES_TXT)
        item = fetcher.enqueue(url, uncomp=self._compressed)
        fetcher.run(progress=progress)
        if item.getStatus() == SUCCEEDED:
            localpath = item.getTargetPath()
            digest = getFileDigest(localpath)
            if digest == self._digest:
                return True
            fetcher.reset()
            url = posixpath.join(self._baseurl, CHECKSUMS_md5)
            item = fetcher.enqueue(url, uncomp=self._compressed)
            gpgurl = posixpath.join(self._baseurl, CHECKSUMS_md5 + ".asc")
            gpgitem = fetcher.enqueue(gpgurl)
            fetcher.run(progress=progress)
            if item.getStatus() == SUCCEEDED:
                checksumpath = item.getTargetPath()
            else:
                checksumpath = None
            self.removeLoaders()
            loader = SlackSiteLoader(localpath, checksumpath, self._baseurl)
            loader.setChannel(self)
            self._loaders.append(loader)
        elif fetcher.getCaching() is NEVER:
            lines = [_("Failed acquiring information for '%s':") % self,
                     u"%s: %s" % (item.getURL(), item.getFailedReason())]
            raise Error, "\n".join(lines)
        else:
            return False

        self._digest = digest

        return True

def create(alias, data):
    return SlackSiteChannel(data["baseurl"],
                            data["compressed"],
                            data["type"],
                            alias,
                            data["name"],
                            data["manual"],
                            data["removable"],
                            data["priority"])

# vim:ts=4:sw=4:et
