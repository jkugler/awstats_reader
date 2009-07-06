
"""Top level object reads the files in the directory.

Ask for object[2009]

Returns list of months it found.

Ask for object[2009][7]

Returns a log file object, from which you can query sections of the stats


"""

import datetime
import glob
import os

def awstats_datetime(date_string):
    pass

class AwstatsReader(object):
    def __init__(self, directory, domain):
        self.__directory = directory
        self.__domain = domain
        self.__years = {}
        self.__year_list = []
        self.__curr_year_index = -1

        for fname in glob.glob(os.path.join(directory, 'awstats??????.' + domain + '.txt')):
            stat_name = os.path.basename(fname)
            year = int(stat_name[9:13])
            month = int(stat_name[7:9])
            if year not in self.__years:
                self.__years[year] = AwstatsYear(self.__domain, year)

            self.__years[year]._set_month(month, AwstatsMonth(year, month, fname))

        self.__year_list = sorted(self.__years.keys())

    def __getitem__(self, year):
        try:
            return self.__years[year]
        except KeyError:
            raise KeyError("Domain '%s' does not have any records for year %s" % (self.__domain, year))

    def __iter__(self):
        return (self.__years[y] for y in self.__year_list)

    def __str__(self):
        return "<AwstatsReader: " + ', '.join([str(y) for y in self.__year_list]) + ">"

class AwstatsYear(object):
    def __init__(self, domain, year):
        self.__domain = domain
        self.__year = year
        self.__months = {}
        self.__month_list = []

    def _set_month(self, month, mobject):
        self.__months[month] = mobject

    def __iter__(self):
        return (self.__months[m] for m in sorted(self.__months.keys()))

    def __getitem__(self,  month):
        try:
            return self.__months[month]
        except KeyError:
            raise KeyError("Domain '%s' does not have any records for year %s, month %s"
                           % (self.__domain, self.__year, month))

    def __str__(self):
        self.month_list = sorted(self.__months.keys())
        return "<AwstatsYear " + str(self.__year) + ": " + ', '.join([str(m) for m in self.__month_list]) + ">"

class AwstatsMonth(object):
    def __init__(self, year, month, fname):
        self.__year = year
        self.__month = month
        self.__version = None
        self.__fname = fname
        self.__pos_map = {}
        self.__section_list = []
        self.__section_cache = {}
        self.__fobject = None

    def __init_file(self):
        self.__fobject = open(self.__fname)

        self.__version = self.__fobject.readline().split()[3]

        for line in self.__fobject:
            if line.startswith('POS_'):
                # The Map lines (and others for that matter) have trailing spaces
                # Truly odd
                k,v = line.split(' ', 1)
                k = k[4:].lower()
                self.__pos_map[k] = int(v)
                self.__section_list.append(k)
            if line.startswith('END_MAP'):
                break

    def __get_section(self, name):
        data = ''
        end_flag = 'END_' + name.upper()
        self.__fobject.seek(self.__pos_map[name])
        lines = int(self.__fobject.readline().split(' ')[1])
        for x in xrange(lines):
            data += self.__fobject.readline()
        return data

    def __iter__(self):
        if not self.__fobject:
            self.__init_file()
        return (s for s in self.__section_list)

    def __getitem__(self, item):
        if not self.__fobject:
            self.__init_file()
        if item not in self.__section_cache:
            self.__section_cache[item] = self.__get_section(item)
        return self.__section_cache[item]

    def __str__(self):
        return "<AwstatsMonth " + str(self.__year) + "/" + str(self.__month).rjust(2, '0') +">"

class AwstatsSection(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return "%s, %s" % (name, data)

__section_format_by_version = {}

__section_format['__default__'] = {
    'general':{
        'LastLine':(('date',awstats_datetime),('line',int),('offset',long),('signature',long)),
        'FirstTime':(('first_time', awstats_datetime)),
        'LastTime':(('last_time',awstats_datetime)),
        'LastUpdate':(('date',awstats_datetime),('parsed',int),('old',int),('new',int),('corrupted',int),('dropped',int)),
        '__default__':(int),
        },
    'time':{},
    'visitor':{},
    'day':{},
    'domain':{},
    'login':{},
    'robot':{},
    'worms':{},
    'emailsender':{},
    'emailreceiver':{},
    'session':{},
    'sider':{},
    'filetypes':{},
    'os':{},
    'browser':{},
    'screensize':{},
    'unknownreferer':{},
    'unknownrefererbrowser':{},
    'origin':{},
    'sereferrals':{},
    'pagerefs':{},
    'searchwords':{},
    'keywords':{},
    'misc':{
        '__default__':(('pages',int),('hits',int),('bandwidth',int))},
    'errors':{},
    'cluster':{},
    'sider_404':{},
}
