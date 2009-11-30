#!/usr/bin/env python

import os
import sys
import unittest

# Set up the test environment
opd = os.path.dirname
lib_dir = opd(opd(opd(os.path.abspath(__file__))))
sys.path.insert(0, lib_dir)

from awstats_reader import tests

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

# Some old quick and dirty tests. Will delete later.
#obj  = AwstatsReader.AwstatsReader('/home/jkugler/tmp/awstats_logs', sys.argv[1])
#print obj
#print obj[2007]
#print obj[2008][6]
#m = obj[2009][7]
#print m['general']
#print m['general']['LastLine']
#print m['general'].LastLine
#print m.general.LastLine
#print m['general']['TotalVisits']
#print m['visitor']['132.115.in-addr.arpa']

#for x,y in m.pagerefs.items():
    #print x, m.pagerefs[x].pages, m.pagerefs[x].hits

