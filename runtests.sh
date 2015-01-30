#!/bin/sh
# Runs the unit test with nose in the virtual environment
.virtualenv/bin/python /usr/bin/nosetests1.1 --with-doctest --with-coverage --where . --where model/ --where tests/ --where rest --cover-tests "$@"
