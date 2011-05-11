#!/bin/sh

coverage run "--omit=/usr/share/*,/usr/local/*,*run_tests*,*cchrc/tests*,*config*" ./run_tests.py
coverage report -m
