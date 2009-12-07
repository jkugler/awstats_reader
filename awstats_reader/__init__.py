
"""
AwstatsReader
A library for querying statistics from AWStats (non-XML) Cache files
"""

import datetime
import glob
import os

# Requires odict from http://www.voidspace.org.uk/python/odict.html
import odict
od = odict.OrderedDict
d = dict

class AwstatsDateTime(datetime.datetime):
    def strftime(self, format):
        # A special flag value used by Awstats Reader
        # It's an (relatively safe) assumption that Awstats Reader won't be
        # processing data from year 1 AD
        # This is used because there are cases where an AWSTats date
        # (or datetime) field may be simply '0'
        if self.year == 1:
            return '0'
        else:
            return datetime.datetime.strftime(self, format)

class AwstatsDate(datetime.date):
    def strftime(self, format):
        # See comment on AwstatsDatetime
        if self.year == 1:
            return '0'
        else:
            return datetime.date.strftime(self, format)

def awstats_datetime(date_string):
    """
    Parses an AWStats Date/Time or Date string and returns a datetime.datetime
    or datetime.date object, respectively.
    """
    date_len = len(date_string)
    if date_len == 14:
        return AwstatsDateTime(int(date_string[0:4]), int(date_string[4:6]), int(date_string[6:8]),
                                 int(date_string[8:10]), int(date_string[10:12]),int(date_string[12:14]))

    elif date_len == 8:
        return AwstatsDate(int(date_string[0:4]), int(date_string[4:6]), int(date_string[6:8]))
    elif  date_len == 1 and date_string == '0':
        # Used if the year is zero. Dates are always compared, never added
        return AwstatsDateTime(1,1,1)
    else:
        raise RuntimeError("Invalid date/time string: '%s'" % date_string)

class AttrDict(odict.OrderedDict):
    """
    Allows dicts to be accessed via dot notation as well as subscripts
    """
    def __getattr__(self, name):
        return self[name]

class AwstatsReader(object):
    """

    """
    years = property(lambda self:self.__year_list)

    def __init__(self, directory, domain):
        self.__directory = directory
        self.__domain = domain
        self.__years = {}
        self.__year_list = []
        self.__curr_year_index = -1

        if not os.path.exists(directory):
            raise OSError((2, 'No such directory: %s' % directory, directory))

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

    def __contains__(self, year):
        return year in self.__year_list

    def __iter__(self):
        return (self.__years[y] for y in self.__year_list)

    def __str__(self):
        return "<AwstatsReader: " + ', '.join([str(y) for y in self.__year_list]) + ">"

class AwstatsYear(object):
    months = property(lambda self:self.__month_list)

    def __init__(self, domain, year):
        self.__domain = domain
        self.__year = year
        self.__months = {}
        self.__month_list = []

    def _set_month(self, month, mobject):
        self.__months[month] = mobject
        self.__month_list.append(month)

    def __iter__(self):
        return (self.__months[m] for m in sorted(self.__months.keys()))

    def __contains__(self, month):
        return month in self.__month_list

    def __getitem__(self,  month):
        try:
            return self.__months[month]
        except KeyError:
            raise KeyError("Domain '%s' does not have any records for year %s, month %s"
                           % (self.__domain, self.__year, month))

    def __str__(self):
        self.__month_list = sorted(self.__months.keys())
        return "<AwstatsYear " + str(self.__year) + ": " + ', '.join([str(m) for m in self.__month_list]) + ">"

    year = property(lambda self:self.__year)

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

        version = self.__fobject.readline().split()[3:6]
        self.__version = (version[0], version[2].replace(')',''))

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

    def __get_raw_section(self, name):
        section_data = odict.OrderedDict()
        k = v = ''
        end_flag = 'END_' + name.upper()
        self.__fobject.seek(self.__pos_map[name])
        lines = int(self.__fobject.readline().split(' ')[1])
        for x in xrange(lines):
            line_data = self.__fobject.readline().strip()
            # Seems to be an off-by-one error in some sections
            if line_data == end_flag:
                break
            k,v = line_data.split(' ', 1)
            section_data[k] = v.split(' ')
        return section_data

    def __get_section(self, name):
        if not self.__fobject:
            self.__init_file()
        try:
            if name not in self.__section_cache:
                self.__section_cache[name] = AwstatsSection(self.__version, name, self.__get_raw_section(name))
            return self.__section_cache[name]
        except KeyError:
            raise KeyError("Section '%s' does not exist" % name)

    def __iter__(self):
        if not self.__fobject:
            self.__init_file()
        return (s for s in self.__section_list)

    def __len__(self):
        if not self.__fobject:
            self.__init_file()
        return len(self.__section_list)

    def keys(self):
        if not self.__fobject:
            self.__init_file()
        return self.__section_list

    version = property(lambda self:self.__version)
    year = property(lambda self:self.__year)
    month = property(lambda self:self.__month)

    __getitem__ = __get_section
    __getattr__ = __get_section


    def __str__(self):
        return "<AwstatsMonth " + str(self.__year) + "/" + str(self.__month).rjust(2, '0') +">"

class AwstatsSection(object):
    def __init__(self, version, section_name, raw_data):
        self.__name = section_name
        self.__format = _section_format['__default__'][section_name]
        self.__data = raw_data

    def __str__(self):
        return "<AwstatsSection %s, %s>" % (self.__name, self.__data)

    def __get_data(self, row_name):
        data = self.__data[row_name]
        if row_name in self.__format:
            format = self.__format[row_name]
        else:
            format = self.__format['__default__']

        if isinstance(format, tuple):
            items = odict.OrderedDict()
            for index, f in enumerate(format):
                if len(f) == 3 and f[2] == 'opt' and len(data) <= index:
                    break
                items[f[0]] = f[1](data[index])
            return AttrDict(items)
        else:
            return format(data[0])

    __getitem__ = __get_data
    __getattr__ = __get_data

    def keys(self):
        return list(self.__iter__())

    def get(self, name, default=None):
        try:
            return self.__get_data(name)
        except KeyError:
            return default

    def __iter__(self):
        return (k for k in self.__data.keys())

    def __len__(self):
        return len(self.__data)

    def items(self):
        return ((k,self.__data[k]) for k in self.__data.keys())

    def get_sort_info(self):
        sort_num = None
        sort_by = None
        sort_reversed = None

        if '__meta__' in self.__format:
            sort_num = self.__format['__meta__'].get('sort', None)
            sort_by = self.__format['__meta__'].get('sortby', None)
            sort_reversed = self.__format['__meta__'].get('reversed', True)

        return (sort_num, sort_by, sort_reversed)

    def __merge_sum(v1, v2):
        return v1 + v2

    def __merge_min(v1, v2):
        return min(v1, v2)

    def __merge_max(v1, v2):
        return max(v1, v2)

    def __merge_latest(v1, v2):
        """
        Right now, I'm assuming that the second set of files specified will
        be the later files. I have an idea for making this better, but haven't
        had time to really think it through and code it up.
        """
        return v2

    merge_funcs = {'sum':__merge_sum, 'min':__merge_min,
                   'max':__merge_max, 'latest':__merge_latest}

    def merge(self, other, row_name, field_name):
        """
        'other' is the other section which we are merging
        """
        if row_name in _section_merge_rules['__default__'][self.__name]:
            merge_rule = _section_merge_rules['__default__'][self.__name][row_name][field_name]
        else:
            merge_rule = _section_merge_rules['__default__'][self.__name]['__default__'][field_name]

        if merge_rule.startswith('repl'):
            c,v = merge_rule.split(':',1)
            return str(v)
        else:
            try:
                return AwstatsSection.merge_funcs[merge_rule](self.get(row_name)[field_name],
                                                              other.get(row_name)[field_name])
            except KeyError:
                raise RuntimeError("Unhandled merge rule for section '%s', row '%s', field '%s': '%s'"
                                   % (self.__name, row_name, field_name, merge_rule))


_section_format = {}

_section_format['__default__'] = {
    'general':{
        'LastLine':(('date',awstats_datetime),('line',int),('offset',long),('signature',long)),
        'FirstTime':(('first_time', awstats_datetime),),
        'LastTime':(('last_time',awstats_datetime),),
        'LastUpdate':(('date',awstats_datetime),('parsed',int),('old',int),('new',int),('corrupted',int),('dropped',int)),
        '__default__':(('value', int),),
        },
    'time':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('not_viewed_pages',int),
                       ('not_viewed_hits',int),('not_viewed_bandwidth',int)),
            '__meta__':{'sort':24, 'sortby':'key_int', 'sort_reversed':False}},
    'visitor':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('last_visit',awstats_datetime,'opt'),
                              ('last_visit_start',awstats_datetime,'opt'),('last_visit_page',str,'opt')),
               '__meta__':{'sort':25, 'sortby':'pages'}},
    'day':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('visits',int)),
           '__meta__':{'sort':31, 'sortby':'key', 'sort_reversed':False}},
    'domain':{'__default__':(('pages',int),('hits',int),('bandwidth',int)),
              '__meta__':{'sort':25, 'sortby':'pages'}},
    'login':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('last_visit',awstats_datetime)),
             '__meta__':{'sort':10, 'sortby':'pages'}},
    'robot':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime),('hits_on_robots',int)),
             '__meta__':{'sort':25, 'sortby':'hits'}},
    'worms':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime)),
             '__meta__':{'sort':5, 'sortby':'hits'}},
    'emailsender':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime)),
                   '__meta__':{'sort':20, 'sortby':'hits'}},
    'emailreceiver':{'__default__':(('hits',int),('bandwidth',int),('last_visit',awstats_datetime)),
            '__meta__':{'sort':20, 'sortby':'hits'}},
    'session':{'__default__':(('value', int),)},
    'sider':{'__default__':(('pages',int),('bandwidth',int),('entry',int),('exit',int)),
            '__meta__':{'sort':25, 'sortby':'pages'}},
    'filetypes':{'__default__':(('hits',int),('bandwidth',int),('bandwidth_without_compression',int),
                                ('bandwidth_after_compression',int))},
    'os':{'__default__':(('value', int),)},
    'browser':{'__default__':(('value', int),)},
    'screensize':{'__default__':(('value', int),)},
    'unknownreferer':{'__default__':(('value', awstats_datetime),)},
    'unknownrefererbrowser':{'__default__':(('value', awstats_datetime),)},
    'origin':{'__default__':(('pages',int),('hits',int)),
              '__meta__':{'sort':5, 'sortby':'key'}},
    'sereferrals':{'__default__':(('pages',int),('hits',int))},
    'pagerefs':{'__default__':(('pages',int),('hits',int)),
                '__meta__':{'sort':25, 'sortby':'pages'}},
    'searchwords':{'__default__':(('value', int),),
                   '__meta__':{'sort':10, 'sortby':'value'}},
    'keywords':{'__default__':(('value', int),),
                '__meta__':{'sort':25, 'sortby':'value'}},
    'misc':{'__default__':(('pages',int),('hits',int),('bandwidth',int))},
    'errors':{'__default__':(('hits',int),('bandwidth',int)),
              '__meta__':{'sort':5, 'sortby':'key_int'}},
    'cluster':{'__default__':(('pages',int),('hits',int),('bandwidth',int))},
    'sider_404':{'__default__':(('hits',int),('last_url_referer',str))},
    'plugin_geoip_city_maxmind':{'__default__':(('pages',int),('hits',int),('bandwidth',int),('last_access',awstats_datetime))},
}

"""
Merges data from two months.  The Rules, as far as I can document from
an AWSTats cache file.
"""
_section_merge_rules = {}
_section_merge_rules['__default__'] = {
    'general':{
        'LastLine':d((('date','max'),('line','max'),('offset','max'),('signature','repl:'))),
        'FirstTime':{'first_time':'min'},
        'LastTime':{'last_time':'max'},
        'LastUpdate':d((('date','max'),('parsed','sum'),('old','sum'),('new','sum'),('corrupted','sum'),('dropped','sum'))),
        '__default__':{'value':'sum'},
        },
    'time':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum'),('not_viewed_pages','sum'),
                       ('not_viewed_hits','sum'),('not_viewed_bandwidth','sum')))},
    'visitor':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum'),('last_visit','max'),
                              ('last_visit_start','max'),('last_visit_page','max')))},
    'day':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum'),('visits','sum')))},
    'domain':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum')))},
    'login':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum'),('last_visit','max')))},
    'robot':{'__default__':d((('hits','sum'),('bandwidth','sum'),('last_visit','max'),('hits_on_robots','sum')))},
    'worms':{'__default__':d((('hits','sum'),('bandwidth','sum'),('last_visit','max')))},
    'emailsender':{'__default__':d((('hits','sum'),('bandwidth','sum'),('last_visit','max')))},
    'emailreceiver':{'__default__':d((('hits','sum'),('bandwidth','sum'),('last_visit','max')))},
    'session':{'__default__':{'value':'sum'}},
    'sider':{'__default__':d((('pages','sum'),('bandwidth','sum'),('entry','sum'),('exit','sum')))},
    'filetypes':{'__default__':d((('hits','sum'),('bandwidth','sum'),('bandwidth_without_compression','sum'),
                                ('bandwidth_after_compression','sum')))},
    'os':{'__default__':{'value':'sum'}},
    'browser':{'__default__':{'value':'sum'}},
    'screensize':{'__default__':{'value':'sum'}},
    'unknownreferer':{'__default__':{'value':'max'}},
    'unknownrefererbrowser':{'__default__':{'value':'max'}},
    'origin':{'__default__':d((('pages','sum'),('hits','sum')))},
    'sereferrals':{'__default__':d((('pages','sum'),('hits','sum')))},
    'pagerefs':{'__default__':d((('pages','sum'),('hits','sum')))},
    'searchwords':{'__default__':{'value':'sum'}},
    'keywords':{'__default__':{'value':'sum'}},
    'misc':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum')))},
    'errors':{'__default__':d((('hits','sum'),('bandwidth','sum')))},
    'cluster':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum')))},
    'sider_404':{'__default__':d((('hits','sum'),('last_url_referer','latest')))},
    'plugin_geoip_city_maxmind':{'__default__':d((('pages','sum'),('hits','sum'),('bandwidth','sum'),('last_access','max')))},
}
