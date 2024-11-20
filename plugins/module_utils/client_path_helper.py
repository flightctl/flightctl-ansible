# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

try:
    import pydantic  # pylint: disable=unused-import
except ImportError as imp_exc:
    raise imp_exc

import sys
from pathlib import Path

# Adjust the Python path to include the generated client
client_path = sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "lib/flightctl_api_client"))
