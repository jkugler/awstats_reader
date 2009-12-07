#!/usr/bin/env python

import os
import sys
import unittest

# Set up the test environment
opd = os.path.dirname
sys.path.insert(0, opd(os.path.abspath(__file__)))

from awstats_reader import tests as awsr_tests

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(awsr_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
