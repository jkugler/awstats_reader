#!/usr/bin/python

# My quick and dirty test script - mostly to verify operation and serve
# as examples

import sys
import AwstatsReader

obj  = AwstatsReader.AwstatsReader('/home/jkugler/tmp/awstats_logs', sys.argv[1])

print obj
print obj[2007]
print obj[2008][6]
m = obj[2009][7]
print m['general']
print m['general']['LastLine']
print m['general'].LastLine
print m.general.LastLine
print m['general']['TotalVisits']
print m['visitor']['132.115.in-addr.arpa']

for x,y in m.pagerefs.items():
    print x, m.pagerefs[x].pages, m.pagerefs[x].hits

