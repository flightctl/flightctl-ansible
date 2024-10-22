# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

STATE_ARG_SPEC = dict(
    state=dict(type="str", default="present", choices=['present', 'absent'])
)
