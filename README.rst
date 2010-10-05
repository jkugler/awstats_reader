ABOUT THE MODULE
================
AwstatsReader is a pythonic interface to AWStats data cache files.  Using it,
you can access year and month via dict-like subscripts, and and individual
data points via both dict-like subscripts and attribute-like accessors.

As of version 0.5, it includes a script for merging AWStats Cache files.

Download: http://azariah.com/open_source.html

ABOUT THE AUTHOR
================
Joshua Kugler (joshua@azariah.com) is a programmer and system administator
with over 10 years of industory experience.
Resume at: http://jjncj.com/papers/KuglerResume.pdf

DISCLAIMER
==========
This is an beta-ish release.  There are 43 tests which cover most, if not
all of the functionality, but not much documentation.  The interface should be
considered stable, but not in concrete.  The usage of this project in a "real
world" situation (awstats_cache_merge.py) led to many improvements to the API.

I wrote this via examples from an AWStats cache file, so I'm sure there are
sections for which I do not have definitions.  If you would send me those
sections, I'll be sure to add them.

Right now, this will parse and display cache files from AWStats 6.5. I've not
tested other versions yet, as 6.5 is the only version I've had access to so far.

REPOSITORY
==========
http://github.com/jkugler/awstats_reader

INSTALLATION
============
See INSTALL

LICENSE
=======
See COPYING

EXAMPLE
=======
Usage is pretty self explanatory::

    import awstats_reader

    obj  = awstats_reader.AwstatsReader('/path/to/awstats_logs', 'example.com')

    print obj[2007]
    print obj[2008][6]
    m = obj[2009][7]
    print m['general']
    # Access like a dictionary...
    print m['general']['LastLine']
    #...or like an object attribute
    print m['general'].LastLine
    print m.general.LastLine

FEEDBACK
========
Please send questions/comments/suggestions to awstatsreader@azariah.com
For now, you can find the latest version here: http://azariah.com/open_source.html
