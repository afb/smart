from cpm.backends.rpm.header import RPMHeaderListLoader
from cpm.repository import Repository
from cpm import *
import posixpath

class RPMHeaderListRepository(Repository):

    def __init__(self, type, name, hdlurl, pkgbaseurl):
        Repository.__init__(self, type, name)
        
        self._hdlurl = hdlurl
        self._pkgbaseurl = pkgbaseurl

    def fetch(self, fetcher):
        fetcher.reset()
        fetcher.enqueue(self._hdlurl)
        fetcher.run("header list for '%s'" % self._name)
        failed = fetcher.getFailedSet()
        if failed:
            logger.warning("failed acquiring header list for '%s': %s" %
                           (self._name, failed[self._hdlurl]))
            logger.debug("%s: %s" % (self._hdlurl, failed[self._hdlurl]))
        else:
            localpath = fetcher.getSucceeded(self._hdlurl)
            self._loader = RPMHeaderListLoader(localpath, self._pkgbaseurl)
            self._loader.setRepository(self)

def create(type, data):
    if hasattr(data, "tag") and data.tag == "repository":
        node = data
        name = node.get("name")
        if not name:
            raise Error, "repository of type '%s' has no name" % type
        hdlurl = None
        pkgbaseurl = None
        for n in node.getchildren():
            if n.tag == "hdlurl":
                hdlurl = n.text
            elif n.tag == "pkgbaseurl":
                pkgbaseurl = n.text
        if not hdlurl:
            raise Error, "repository '%s' has no hdlurl" % name
        if not pkgbaseurl:
            raise Error, "repository '%s' has no pkgbaseurl" % name
        return RPMHeaderListRepository(type, name, hdlurl, pkgbaseurl)
    else:
        raise RepositoryDataError

# vim:ts=4:sw=4:et