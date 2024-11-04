# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class FlightctlException(Exception):
    pass


class FlightctlHTTPException(FlightctlException):
    pass


class ConfigFileException(FlightctlException):
    pass


class ValidationException(FlightctlException):
    pass
