
"""Top level object reads the files in the directory.

Ask for object[2009]

Returns list of months it found.

Ask for object[2009][7]

Returns a log file object, from which you can query sections of the stats


"""

import glob
import os

class AwstatsReader(object):
    def __init__(self, directory, domain):
        self.directory = directory
        self.domain = domain
        self.years = {}
        self.year_list = []
        self.curr_year_index = -1

        for fname in glob.glob(os.path.join(directory, 'awstats??????.' + domain + '.txt')):
            stat_name = os.path.basename(fname)
            year = int(stat_name[9:13])
            month = int(stat_name[7:9])
            if year not in self.years:
                self.years[year] = AwstatsYear(year)

            self.years[year]._set_month(month, AwstatsMonth(year, month, fname))

        self.year_list = sorted(self.years.keys())

    def __getitem__(self, year):
        return self.years[year]

    def __iter__(self):
        self.curr_year_index = -1
        return self

    def next(self):
        try:
            self.curr_year_index += 1
            return self.years[self.year_list[self.curr_year_index]]
        except IndexError:
            raise StopIteration

    def __str__(self):
        return "<AwstatsReader: " + ', '.join([str(y) for y in self.year_list]) + ">"

class AwstatsYear(object):
    def __init__(self, year):
        self.year = year
        self.months = {}
        self.month_list = []
        self.curr_month_index = -1

    def _set_month(self, month, mobject):
        self.months[month] = mobject

    def __iter__(self):
        self.month_list = sorted(self.months.keys())
        self.curr_month_index = -1
        return self

    def __getitem__(self, item):
        return self.months[item]

    def next(self):
        try:
            self.curr_month_index += 1
            return self.months[self.month_list[self.curr_month_index]]
        except IndexError:
            raise StopIteration

    def __str__(self):
        self.month_list = sorted(self.months.keys())
        return "<AwstatsYear " + str(self.year) + ": " + ', '.join([str(m) for m in self.month_list]) + ">"

class AwstatsMonth(object):
    def __init__(self, year, month, fname):
        self.year = year
        self.month = month
        self.fname = fname
        self.pos_map = {}
        self.section_cache = {}
        self.fobject = None

    def __init_file(self):
        self.fobject = open(self.fname)

        for line in self.fobject:
            if line.startswith('POS_'):
                # The Map lines (and others for that matter) have trailing spaces
                # Truly odd
                k,v = line.split(' ', 1)
                self.pos_map[k[4:].lower()] = int(v)
            if line.startswith('END_MAP'):
                break

    def __get_section(self, name):
        data = ''
        end_flag = 'END_' + name.upper()
        self.fobject.seek(self.pos_map[name])
        lines = int(self.fobject.readline().split(' ')[1])
        for x in xrange(lines):
            data += self.fobject.readline()

        return data

    def __getitem__(self, item):
        if not self.fobject:
            self.__init_file()
        if item not in self.section_cache:
            self.section_cache[item] = self.__get_section(item)
        return self.section_cache[item]


    def __str__(self):
        return "<AwstatsMonth " + str(self.year) + "/" + str(self.month).rjust(2, '0') +">"


class AwstatsSection(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return "%s, %s" % (name, data)

section_format = {}
section_format['default'] = {}