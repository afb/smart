from cpm.option import OptionParser
from cpm import *
import string
import re

USAGE="cpm flag [options]"

def parse_options(argv):
    parser = OptionParser(usage=USAGE)
    parser.add_option("--set", action="store_true",
                      help="set flag given as first argument for "
                           "'name relation version' given in the following "
                           "arguments")
    parser.add_option("--remove", action="store_true",
                      help="unset flag given as first argument for "
                           "'name relation version' given in the following "
                           "arguments")
    parser.add_option("--show", action="store_true",
                      help="show packages with the flags given as arguments "
                           "or all flags if no argument was given")
    parser.add_option("--force", action="store_true",
                      help="ignore problems")
    opts, args = parser.parse_args(argv)
    opts.args = args
    return opts

TARGETRE = re.compile(r"^\s*(?P<name>\S+)\s*"
                      r"((?P<rel>[<>=]+)\s*"
                      r"(?P<version>\S+))?\s*$")

def main(opts, ctrl):
    pkgflags = sysconf.get("package-flags")
    if pkgflags is None:
        pkgflags = {}
        sysconf.set("package-flags", pkgflags)

    if opts.set or opts.remove:

        if len(opts.args) < 2:
            raise Error, "no flag name or target provided"

        flag = opts.args[0].strip()

        for arg in opts.args[1:]:

            m = TARGETRE.match(arg)
            if not m:
                raise Error, "invalid target: %s" % arg

            g = m.groupdict()

            names = pkgflags.setdefault(flag, {})
            lst = names.setdefault(g["name"], [])

            tup = (g["rel"], g["version"])

            if opts.set:
                if tup not in lst:
                    lst.append(tup)
            else:
                if tup in lst:
                    lst.remove(tup)

        if opts.remove and pkgflags.get(flag) == {}:
            del pkgflags[flag]

    elif opts.show:

        flags = opts.args or pkgflags

        for flag in flags:
            flag = flag.strip()

            print flag

            names = pkgflags.get(flag, {})
            for name in names:
                for relation, version in names[name]:
                    if relation and version:
                        print "   ", name, relation, version
                    else:
                        print "   ", name
            print

# vim:ts=4:sw=4:et