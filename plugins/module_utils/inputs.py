# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass
from typing import Optional

from .constants import ResourceType
from .exceptions import ValidationException


@dataclass
class ApprovalInput:
    resource: ResourceType
    name: str
    approved: bool
    approved_by: Optional[str] = None
    labels: Optional[dict] = None

    def __post_init__(self):
        if self.resource not in [ResourceType.CSR, ResourceType.ENROLLMENT]:
            raise ValidationException(f"Kind {self.resource.value} does not support approval")
        if not self.name:
            raise ValidationException("Name must be specified")
        if self.approved is None:
            raise ValidationException("Approved must be specified")

    def to_request_params(self):
        params = dict(
            approved=self.approved,
        )
        if self.approved_by:
            params['approvedBy'] = self.approved_by
        if self.labels:
            params['labels'] = self.labels
        return params
