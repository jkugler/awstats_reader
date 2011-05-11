#!/usr/bin/env python

import operator
import optparse
import os
import sys
import time

from awstats_reader import (AwstatsReader as ar, AwstatsDateTime, AwstatsDate,
                            make_get_field)
from odict import OrderedDict as od

ap = os.path.abspath

__version___ = '0.1'

def get_opts():

    usage = 'usage: %prog --dir1=/path/to/dir1 --domain1=example.com [other options]'
    parser = optparse.OptionParser(usage=usage, version='%prog ' + __version___)
    a = parser.add_option
    a('-v', action='count', dest='verbose', help='Verbose. Specify more than once '
      'for more verbosity')
    a('--dir1', dest='dir1', default='.',
      help='First (or only) directory of cache files')
    a('--domain1', dest='domain1', default=None, help='First domain to merge')
    a('--dir2', dest='dir2', default=None, help='Second directory of cache files. '
      'Defaults to dir1 if not specified.  If not specified, dir1 and dir2 '
      'must be different')
    a('--domain2', dest='domain2', default=None,
      help='Second domain to merge. Defaults to domain1 if not specified. If not '
      'specified, domain1 and domain2 must be different',)
    a('--outdomain', dest='outdomain', default=None, help='Domain name for output files.')
    a('--outdir', dest='outdir', default=None, help='Directory for output files')


    # Some sanity checking
    (opts, args) = parser.parse_args()

    if opts.outdir is None:
        parser.error('Outdomain and Outdir must be specified')

    if opts.domain1 is None:
        parser.error('domain1 must be specified')

    if ((opts.domain2 is None or opts.domain1 == opts.domain2) and
        (opts.dir2 is None or ap(opts.dir1) == ap(opts.dir2))):
        parser.error('If domain2 is the same as domain1, dir2 must be different than dir1, and vice versa.')

    if opts.domain2 is None:
        opts.domain2 = opts.domain1

    if opts.dir2 is None:
        opts.dir2 = opts.dir1

    if opts.outdomain is None:
        opts.outdomain = opts.domain1

    if opts.outdomain == opts.domain1 and ap(opts.outdir) == ap(opts.dir1):
        parser.error('Domain1 and outdomain cannot be the same when outdir and dir1 are the same')

    if opts.outdomain == opts.domain2 and ap(opts.outdir) == ap(opts.dir2):
        parser.error('Domain1 and outdomain cannot be the same when outdir and dir1 are the same')

    return (opts, args)

def write_file(dest_dir, domain, year, month, data, version):
    month = '%02d' % month
    out_file_name = os.path.join(dest_dir, 'awstats' + month + str(year) + '.' + domain + '.txt')

    outfile = open(out_file_name, 'w')

    outfile.write('AWSTATS DATA FILE %s (build %s)\n\n' % version)

    for section in data.keys():
        outfile.write('BEGIN_' + section.upper() + ' ' + str(len(data[section])) + '\n')
        for row in data[section]:
            row_data = []
            row_data.append(row) # The row name/key
            for field in data[section][row]:
                v = data[section][row][field]
                if isinstance(v, AwstatsDateTime):
                    row_data.append(v.strftime('%Y%m%d%H%M%S'))
                elif isinstance(v, AwstatsDate):
                    row_data.append(v.strftime('%Y%m%d'))
                else:
                    row_data.append(v)
            outfile.write(' '.join([str(x) for x in row_data]) + '\n')

        outfile.write('END_' + section.upper() + '\n')
        outfile.write('\n')

    outfile.close()

def merge_month(m1, m2):
    """
    Merges data from two months.
    """
    data = od()
    # We do this to keep ordering. sets (and set unions) aren't order stable
    sections = od([(k, True) for k in m1.keys()])
    sections.update(od([(k, True) for k in m2.keys()]))

    for section in sections:
        data[section] = od()

        s1 = m1[section]
        s2 = m2[section]

        rows = od([(k, True) for k in s1.keys()])
        rows.update(od([(k, True) for k in s2.keys()]))
        for row_name in rows:
            d1 = s1.get(row_name)
            d2 = s2.get(row_name)

            if d1 is None or d2 is None:
                data[section][row_name] = d1 or d2
                continue
            else:
                data[section][row_name] = od()

            # Some rows have optional fields.
            if len(d1) >= len(d2):
                field_list = d1.keys()
            else:
                field_list = d2.keys()

            for field in field_list:
                data[section][row_name][field] = od()
                # Again, those options fields
                if field not in d1:
                    data[section][row_name][field] = d2[field]
                    continue
                elif field not in d2:
                    data[section][row_name][field] = d1[field]
                    continue
                data[section][row_name][field] = s1.merge(s2, row_name, field)

        sort_num, sort_by, sort_reversed = s1.get_sort_info()
        if sort_num:
            if sort_by == 'key':
                data[section] = od(sorted(data[section].iteritems()))
            elif sort_by == 'key_int':
                data[section] = od(sorted(data[section].iteritems(), key=lambda x: int(x[0])))
            else:
                data[section] = od(sorted(data[section].iteritems(), key=awmake_get_field(sort_by), reverse=sort_reversed))

    return data


def main():
    """
    Get all the years and months, cycles through them, calling merge_month
    to do the main part of the work.
    """
    (opts, args) = get_opts()

    # TODO: Need to get a version string
    dom1 = ar(opts.dir1, opts.domain1)
    dom2 = ar(opts.dir2, opts.domain2)

    years = set(dom1.years).union(dom2.years)

    for year in years:
        months = set()
        if year in dom1:
            months = months.union(dom1[year].months)
        if year in dom2:
            months= months.union(dom1[year].months)

        for  month in months:
            if year not in dom1 or month not in dom1[year]:
                write_file(opts.outdir, opts.outdomain, year, month, dom2)
                continue
            if year not in dom2 or month not in dom2[year]:
                write_file(opts.outdir, opts.outdomain, year, month, dom1)
                continue

            data = merge_month(dom1[year][month], dom2[year][month])
            version = sorted((dom1[year][month].version, dom2[year][month].version), reverse=True)[0]

            write_file(opts.outdir, opts.outdomain, year, month, data, version)

if __name__ == '__main__':
    main()