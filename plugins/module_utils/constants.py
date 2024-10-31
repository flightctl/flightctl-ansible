# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from enum import Enum


# TODO expand Kind to include additional types  # pylint: disable=fixme
class Kind(Enum):
    ENROLLMENT = "EnrollmentRequest"
    CSR = "CertificateSigningRequest"
