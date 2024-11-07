# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass, field
from typing import List, Optional

from .constants import Kind
from .exceptions import ValidationException


@dataclass
class ApprovalInput:
    kind: Kind
    name: str
    approved: bool
    approved_by: Optional[str] = None
    labels: Optional[dict] = None

    def __post_init__(self):
        if self.kind not in [Kind.CSR, Kind.ENROLLMENT]:
            raise ValidationException(f"Kind {self.kind.value} does not support approval")
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


# TODO change to 'Options' rather than input and better enforce link between these options and the api module?
@dataclass
class InfoInput:
    kind: Kind
    name: str
    label_selector: Optional[str] = None
    field_selector: Optional[str] = None
    owner: Optional[str] = None
    fleet_name: Optional[str] = None
    rendered: Optional[bool] = None
    summary: Optional[bool] = None
    summary_only: Optional[bool] = None
    status_filter: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    continue_token: Optional[str] = None

    def __post_init__(self):
        if not self.kind:
            raise ValidationException("Kind must be specified")
        if self.owner and self.kind not in [Kind.DEVICE, Kind.FLEET]:
            raise ValidationException(f"Owner field is only valid for Device and Fleet kinds")
        if self.rendered and self.kind is not Kind.DEVICE:
            raise ValidationException(f"Rendered field is only valid for Device kind")
        if self.fleet_name and self.kind is not Kind.TEMPLATE_VERSION:
            raise ValidationException(f"Fleet name field is only valid for TemplateVersion kind")
        if self.summary_only:
            if self.kind is not Kind.DEVICE:
                raise ValidationException(f"Summary Only field is only valid for Device kind")
            if self.name:
                raise ValidationException(f"Summary Only field is not valid when fetching one Device")
        if self.summary:
            if self.kind is not Kind.FLEET:
                raise ValidationException(f"Summary field is only valid for Fleet kind")
            if not self.name:
                raise ValidationException(f"Summary field is only valid when fetching one Fleet")
        if self.status_filter:
            if self.kind is not Kind.DEVICE:
                raise ValidationException(f"Status filter field is only valid for Device kind")
            if self.name:
                raise ValidationException(f"Status filter field is not valid when fetching one Device")
        if self.label_selector and self.name:
            raise ValidationException(f"Label selector field is not valid when fetching one resource")
        if self.field_selector and self.name:
            raise ValidationException(f"Label selector field is not valid when fetching one resource")

    def to_request_params(self):
        params = dict()
        if self.label_selector:
            params['labelSelector'] = self.label_selector
        if self.field_selector:
            params['fieldSelector'] = self.field_selector
        if self.owner:
            params['owner'] = self.owner
        if self.summary:
            params['addDevicesSummary'] = self.summary
        if self.summary_only:
            params['summaryOnly'] = self.summary_only
        if self.limit:
            params['limit'] = self.limit
        if self.continue_token:
            params['continue'] = self.continue_token
        if self.status_filter:
            params['statusFilter'] = self.status_filter
        return params
