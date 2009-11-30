#!/usr/bin/env python

import unittest

import awstats_reader

class TestAwstatsReader(unittest.TestCase):
    """Tests the AwstatsReader main object"""

    def test_init(self):
        """Make sure we can initialize the class"""
        ar = awstats_reader.AwstatsReader('/tmp', 'example.com')
        self.assertTrue(isinstance(ar, awstats_reader.AwstatsReader))

    def test_get_year_fail(self):
        """Getting an invalid year raises an exception"""
        ar = awstats_reader.AwstatsReader('/tmp', 'example.com')
        self.assertRaises(KeyError, ar.__getitem__, 9999)

class TestAwstatsYear(unittest.TestCase):
    pass

class TestAwstatsMonth(unittest.TestCase):
    pass

class TestAwstatsSection(unittest.TestCase):
    pass

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

