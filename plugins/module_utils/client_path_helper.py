# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import sys
from pathlib import Path

try:
    # Adjust the Python path to include the generated client
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "lib/flightctl_api_client"))
except ImportError as imp_exc:
    # Handled elsewhere
    pass
