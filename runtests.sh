#!/bin/sh
# Runs the unit test with nose in the virtual environment
.virtualenv/bin/python /usr/bin/nosetests test.py "$@"
