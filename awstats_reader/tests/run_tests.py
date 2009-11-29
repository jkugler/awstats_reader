#!/usr/bin/env python

import os
import sys
import unittest

lib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, lib_dir)






if __name__ == '__main__':
    unittest.main()