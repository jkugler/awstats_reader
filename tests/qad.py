#!/usr/bin/python

# My quick and dirty test script

import AwstatsReader

obj  = AwstatsReader.AwstatsReader('/home/jkugler/tmp/awstats_logs', 'gwscientific.com')

print obj
print obj[2007]
print obj[2008][6]
m = obj[2009][7]
print m['general']
