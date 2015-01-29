#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of REDHAWK rest-python.
#
# REDHAWK rest-python is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# REDHAWK rest-python is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
from tornado.testing import main
import unittest
import doctest

from tests import *

from model import domain

def all():
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    # Add domain doctests
    suite.addTests(doctest.DocTestSuite(domain))
    return suite


if __name__ == '__main__':
    # FIXME: Make unit test usable
    # 1) direct output for working tests to a file, hide from console
    # 2) be able to run specific tests easily
    # 3) list the tests available
    main()
