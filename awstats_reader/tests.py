#!/usr/bin/env python

import datetime
import os
import unittest

import awstats_reader

opd = os.path.dirname

test_file_dir = os.path.join(opd(opd(os.path.abspath(__file__))), 'test_files')

class TestAwstats(unittest.TestCase):
    """Tests various helper functions in the awstats_reader package"""

    def test_14_digit_datetime(self):
        """Ensure date/time strings are being evaluated correctly"""
        obj = awstats_reader.awstats_datetime('20091130165230')
        dt = datetime.datetime(2009, 11, 30, 16, 52, 30)
        self.assertEqual(obj, dt)

    def test_8_digit_date(self):
        """Ensure date strings are being evaluated correctly"""
        obj = awstats_reader.awstats_datetime('20091130')
        dt = datetime.date(2009, 11, 30)
        self.assertEqual(obj, dt)

    def test_14_digit_datetime_detection(self):
        """Ensure the AwstatsDateTime object is returned"""
        obj = awstats_reader.awstats_datetime('20091130165230')
        self.assertTrue(isinstance(obj, awstats_reader.AwstatsDateTime))

    def test_8_digit_date_detection(self):
        """Ensure the AwstatsDate object is returned"""
        obj = awstats_reader.awstats_datetime('20091130')
        self.assertTrue(isinstance(obj, awstats_reader.AwstatsDate))

    def test_year_year_zero_datetime_parse(self):
        """Ensure the Awstats 'year zero' is parsed correctly"""
        obj = awstats_reader.awstats_datetime('0')
        self.assertEqual(obj,datetime.datetime(1,1,1))

    def test_year_zero_datetime_output(self):
        """Ensure the Awstats 'year zero' is printed correctly"""
        obj = awstats_reader.awstats_datetime('0')
        self.assertEqual(obj.strftime('%Y%m%d%H%M%S'), '0')

    def test_datetime_invalid_string(self):
        """Ensure an invalid date/time string raises an exception"""
        self.assertRaises(RuntimeError, awstats_reader.awstats_datetime, '2009')

    def test_attr_dict(self):
        """Ensure AttrDict behaves correctly"""
        obj = awstats_reader.AttrDict([('this','that'), ('thus','those')])
        self.assertEqual(obj.thus, 'those')

class TestAwstatsReader(unittest.TestCase):
    """Tests the AwstatsReader main object"""

    def test_init(self):
        """Ensure we can initialize the class"""
        ar = awstats_reader.AwstatsReader('/tmp', 'example.com')
        self.assertTrue(isinstance(ar, awstats_reader.AwstatsReader))

    def test_invalid_year_fail(self):
        """Ensure getting an invalid year raises an exception"""
        ar = awstats_reader.AwstatsReader('/tmp', 'example.com')
        self.assertRaises(KeyError, ar.__getitem__, 9999)

    def test_valid_year(self):
        """Ensure getting a valid year returns an AwstatsYear object"""
        ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')
        obj = ar[2009]
        self.assertTrue(isinstance(obj, awstats_reader.AwstatsReader))

    def test_invalid_dir(self):
        """Ensure passing an invalid directory raises an exception"""
        self.assertRaises(IOError, awstats_reader.AwstatsReader, '/tmp/XYZ', 'example.com')

class TestAwstatsYear(unittest.TestCase):
    pass

class TestAwstatsMonth(unittest.TestCase):
    pass

class TestAwstatsSection(unittest.TestCase):
    pass

class TestAwstatsMerge(unittest.TestCase):
    """Test functions and procedures in awstats_cache_merge"""

    def test_make_get_field(self):
        """Ensure make_get_field constructs a function which returns the proper value"""
        import odict
        import awstats_cache_merge

        od = odict.OrderedDict([('pages', 4), ('hits', 15), ('bandwidth', 386873)])

        f = awstats_cache_merge.make_get_field('bandwidth')

        self.assertEqual(f(('dz', od)), 386873)

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

