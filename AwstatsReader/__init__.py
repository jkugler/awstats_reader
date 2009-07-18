
"""Top level object reads the files in the directory.

Ask for object[2009]

Returns list of months it found.

Ask for object[2009][7]

Returns a log file object, from which you can query sections of the stats


"""

import datetime
import glob
import os

from odict import OrderedDict

def awstats_datetime(date_string):
    # 20090718035227
    # 20090701
    if len(date_string) == 14:
        return datetime.datetime(int(date_string[0:4]), int(date_string[4:6]), int(date_string[6:8]),
                                 int(date_string[8:10]), int(date_string[10:12]),int(date_string[12:14]))

    elif len(date_string) == 8:
        return datetime.date(int(date_string[0:4]), int(date_string[4:6]), int(date_string[6:8]))
    else:
        raise RuntimeError("Invalid date/time string: '%s'" % date_string)

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
        section_data = OrderedDict()
        k = v = ''
        end_flag = 'END_' + name.upper()
        self.__fobject.seek(self.__pos_map[name])
        lines = int(self.__fobject.readline().split(' ')[1])
        for x in xrange(lines):
            k,v = self.__fobject.readline().strip().split(' ', 1)
            section_data[k] = v.split(' ')
        return section_data

    def __iter__(self):
        if not self.__fobject:
            self.__init_file()
        return (s for s in self.__section_list)

    def __getitem__(self, item):
        if not self.__fobject:
            self.__init_file()
        try:
            if item not in self.__section_cache:
                self.__section_cache[item] = AwstatsSection(item, self.__get_section(item))
            return self.__section_cache[item]
        except KeyError:
            raise KeyError("Section '%s' does not exist" % item)

    def __str__(self):
        return "<AwstatsMonth " + str(self.__year) + "/" + str(self.__month).rjust(2, '0') +">"

class AwstatsSection(object):
    def __init__(self, name, raw_data):
        self.name = name
        self.format = _section_format['__default__'][name]
        self.data = raw_data

    def __str__(self):
        return "<AwstatsSection %s, %s>" % (self.name, self.data)

    def __get_data(self, name):
        data = self.data[name]
        if name in self.format:
            format = self.format[name]
        else:
            format = self.format['__default__']

        if len(format) > 1:
            items = {}
            for index, f in enumerate(format):
                if len(f) == 3 and f[2] == 'opt' and len(data) <= index:
                    break
                items[f[0]] = f[1](data[index])
            return items
        else:
            return format[0](data)

    def __getitem__(self, name):
        return self.__get_data(name)

_section_format = {}

_section_format['__default__'] = {
    'general':{
        'LastLine':(('date',awstats_datetime),('line',int),('offset',long),('signature',long)),
        'FirstTime':(('first_time', awstats_datetime)),
        'LastTime':(('last_time',awstats_datetime)),
        'LastUpdate':(('date',awstats_datetime),('parsed',int),('old',int),('new',int),('corrupted',int),('dropped',int)),
        '__default__':(int),
        },
    'time':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('not_viewed_pages',int),
                       ('not_viewed_hits',int),('not_viewed_bandwidth',int))},
    'visitor':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('last_visit',awstats_datetime,'opt'),
                              ('last_visit_start',awstats_datetime,'opt'),('last_visit_page',str,'opt'))},
    'day':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('visits',int))},
    'domain':{'__default__':(('pages',int),('hits',int),('bandwidth',int))},
    'login':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('last_visit',awstats_datetime))},
    'robot':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime),('hits_on_robots',int))},
    'worms':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime))},
    'emailsender':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime))},
    'emailreceiver':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime))},
    'session':{'__default__':(int)},
    'sider':{'__default__':(('pages',int),('bandwidth',int),('entry',int),('exit',int))},
    'filetypes':{'__default__':(('hits',int),('bandwidth',int),('bandwidth_without_compression',int),
                                ('bandwidth_after_compression',int))},
    'os':{'__default__':(int)},
    'browser':{'__default__':(int)},
    'screensize':{}, # ???????????????
    'unknownreferer':{'__default__':(awstats_datetime)},
    'unknownrefererbrowser':{'__default__':(awstats_datetime)},
    'origin':{'__default__':(('pages',int),('hits',int))},
    'sereferrals':{'__default__':(('pages',int),('hits',int))},
    'pagerefs':{'__default__':(('pages',int),('hits',int))},
    'searchwords':{'__default__':(int)},
    'keywords':{'__default__':(int)},
    'misc':{'__default__':(('pages',int),('hits',int),('bandwidth',int))},
    'errors':{'__default__':(('hits',int),('bandwidth',int))},
    'cluster':{'__default__':(('pages',int),('hits',int),('bandwidth',int))},
    'sider_404':{'__default__':(('hits',int),('last_url_referer',str))},
    'plugin_geoip_city_maxmind':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('last_access',awstats_datetime))},
}
