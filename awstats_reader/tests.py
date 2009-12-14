#!/usr/bin/env python

import datetime
import os
import types
import unittest

import awstats_reader

opd = os.path.dirname

test_file_dir = os.path.join(opd(opd(os.path.abspath(__file__))), 'test_files')

class TestAwstatsHelpers(unittest.TestCase):
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
        self.assertTrue(isinstance(obj, awstats_reader.AwstatsYear))

    def test_invalid_dir(self):
        """Ensure passing an invalid directory raises an exception"""
        self.assertRaises(OSError, awstats_reader.AwstatsReader, '/tmp/XYZ', 'example.com')

    def test_iter_operation(self):
        """Ensure AwstatsYear's __iter__ function is working"""
        ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')
        year_iter = ar.__iter__()
        self.assertTrue(isinstance(year_iter, types.GeneratorType))

    def test_found_all_years(self):
        """Ensure all years were found"""
        ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')
        self.assertEqual(ar.years, [2008,2009])

    def test_iter_all_years(self):
        """Ensure year iterator is working"""
        ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')
        self.assertEqual([ary.year for ary in ar], [2008,2009])

    def test_contains_true(self):
        """Ensure __contains__ is working positively"""
        ary = self.ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')[2009]
        self.assertTrue(11 in ary)

    def test_contains_false(self):
        """Ensure __contains__ is working negatively"""
        ary = self.ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')[2009]
        self.assertFalse(10 in ary)

    def test_str(self):
        """Ensure AwstatsReader __str__ is operating correctly"""
        ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')
        self.assertEqual(str(ar), '<AwstatsReader: 2008, 2009>')


class TestAwstatsYear(unittest.TestCase):

    def setUp(self):
        self.ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')

    def test_invalid_month(self):
        """Ensure getting an invalid month raises an exception"""
        ar_year = self.ar[2009]
        self.assertRaises(KeyError, ar_year.__getitem__, 1)

    def test_valid_month(self):
        """Ensure getting a valid month returns an AwstatsMonth object"""
        ar_month = self.ar[2009][11]
        self.assertTrue(isinstance(ar_month, awstats_reader.AwstatsMonth))

    def test_found_all_months(self):
        """Ensure all months were found"""
        ary = self.ar[2009]
        self.assertEqual(ary.months, [11,12])

    def test_iter_all_months(self):
        """Ensure month is working"""
        ary = self.ar[2009]
        self.assertEqual([arm.month for arm in ary], [11,12])

    def test_str(self):
        """Ensure AwstatsYear __str__ is operating correctly"""
        ary = self.ar[2009]
        self.assertEqual(str(ary), '<AwstatsYear 2009: 11, 12>')


class TestAwstatsMonth(unittest.TestCase):
    wanted_sections = ['general', 'time', 'visitor', 'day', 'domain',
                       'login', 'robot', 'worms', 'emailsender',
                       'emailreceiver', 'session', 'sider', 'filetypes', 'os',
                       'browser', 'screensize', 'unknownreferer',
                       'unknownrefererbrowser', 'origin', 'sereferrals',
                       'pagerefs', 'searchwords', 'keywords', 'misc', 'errors',
                       'cluster', 'sider_404', 'plugin_geoip_city_maxmind']

    def setUp(self):
        self.ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')

    def test_month_iterator(self):
        """Ensure all sections are found"""
        arm = self.ar[2009][11]
        self.assertEqual(list(arm), self.__class__.wanted_sections)

    def test_month_keys(self):
        """Ensure all sections are found"""
        arm = self.ar[2009][11]
        self.assertEqual(arm.keys(), self.__class__.wanted_sections)

    def test_get_invalid_section(self):
        """Ensure getting an invalid sections raises an exception"""
        arm = self.ar[2009][11]
        self.assertRaises(KeyError, arm.__getitem__, 'invalid_section')

    def test_get_valid_section(self):
        """Ensure getting an valid section resturns an AwstatsSection object"""
        arm = self.ar[2009][11]
        ars = arm['general']
        self.assertTrue(isinstance(ars, awstats_reader.AwstatsSection))

    def test_len(self):
        """Ensure the len() function returns the correct value"""
        arm = self.ar[2009][11]
        self.assertEqual(len(arm.keys()), len(self.__class__.wanted_sections))

    def test_str(self):
        """Ensure AwstatsMonth __str__ is operating correctly"""
        arm = self.ar[2009][11]
        self.assertEqual(str(arm), '<AwstatsMonth 2009-11>')

class TestAwstatsSection(unittest.TestCase):
    wanted_lines = ['LastLine', 'FirstTime', 'LastTime', 'LastUpdate',
                    'TotalVisits', 'TotalUnique', 'MonthHostsKnown',
                    'MonthHostsUnknown']

    def setUp(self):
        self.ar = awstats_reader.AwstatsReader(test_file_dir, 'jjncj.com')

    def test_get_valid_line(self):
        """Ensure getting a valid line returns an ordered dict"""
        ars = self.ar[2009][11]['general']
        self.assertTrue(isinstance(ars['TotalVisits'], awstats_reader.AttrDict))

    def test_get_invalid_line(self):
        """Ensure getting an invalid line raises an exception"""
        ars = self.ar[2009][11]['general']
        self.assertRaises(KeyError, ars.__getitem__, 'invalid_section')

    def test_section_iterator(self):
        """Ensure the section iterator works"""
        ars = self.ar[2009][11]['general']
        self.assertEqual(list(ars), self.__class__.wanted_lines)

    def test_section_keys(self):
        """Ensure the section keys works"""
        ars = self.ar[2009][11]['general']
        self.assertEqual(ars.keys(), self.__class__.wanted_lines)

    def test_get_return_default(self):
        """Ensure get() returns the default default value"""
        ars = self.ar[2009][11]['general']
        self.assertTrue(ars.get('invalid_row') is None)

    def test_get_return_default_provided(self):
        """Ensure get() returns the provided default value"""
        ars = self.ar[2009][11]['general']
        self.assertEqual(ars.get('invalid_row', 'ZZZZZZ'), 'ZZZZZZ')

    def test_get_return_desired_value(self):
        """Ensure get() returns the desired value"""
        ars = self.ar[2009][11]['general']
        self.assertEqual(ars.get('TotalVisits'),
                         awstats_reader.AttrDict([('value', 1475)]))

    def test_get_sort_info(self):
        """Ensure sort_info() returns the correct value"""
        ars = self.ar[2009][11]['day']
        self.assertEqual(ars.get_sort_info(), (31, 'key', True))

    def test_merge_max(self):
        """Test max merge operation"""
        ars = self.ar[2009][11]['general']
        ars2 = awstats_reader.AwstatsReader(test_file_dir,
                                            'joshuakugler.com')[2009][11]['general']
        self.assertEqual(ars.merge(ars2, 'LastLine', 'line'), 1011585)

    def test_merge_repl(self):
        """Test repl merge operation"""
        ars = self.ar[2009][11]['general']
        ars2 = awstats_reader.AwstatsReader(test_file_dir,
                                            'joshuakugler.com')[2009][11]['general']
        self.assertEqual(ars.merge(ars2, 'LastLine', 'signature'), '')

    def test_merge_min(self):
        """Test min merge operation"""
        ars = self.ar[2009][11]['general']
        ars2 = awstats_reader.AwstatsReader(test_file_dir,
                                            'joshuakugler.com')[2009][11]['general']
        self.assertEqual(ars.merge(ars2, 'FirstTime', 'first_time'),
                         awstats_reader.AwstatsDateTime(2009, 11, 1, 0, 2, 37))

    def test_merge_sum(self):
        """Test sum merge operation"""
        ars = self.ar[2009][11]['general']
        ars2 = awstats_reader.AwstatsReader(test_file_dir,
                                            'joshuakugler.com')[2009][11]['general']
        self.assertEqual(ars.merge(ars2, 'LastUpdate', 'parsed'), 1262637)

    def test_merge_latest(self):
        """Test 'latest' merge operation"""
        ars = self.ar[2009][11]['sider_404']
        ars2 = awstats_reader.AwstatsReader(test_file_dir,
                                            'joshuakugler.com')[2009][11]['sider_404']
        self.assertEqual(ars.merge(ars2, '/styles/widgets/blog-widget.css',
                                   'last_url_referer'), 'http://joshuakugler.com/')

class TestAwstatsMerge(unittest.TestCase):
    """Test functions and procedures in awstats_cache_merge"""

    def test_make_get_field(self):
        """Ensure make_get_field constructs a function which returns the proper value"""
        import odict
        import awstats_cache_merge

        od = odict.OrderedDict([('pages', 4), ('hits', 15), ('bandwidth', 386873)])

        f = awstats_cache_merge.make_get_field('bandwidth')

        self.assertEqual(f(('dz', od)), 386873)
