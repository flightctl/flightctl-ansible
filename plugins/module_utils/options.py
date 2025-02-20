# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass, field
from typing import List, Optional

from .constants import ResourceType
from .exceptions import ValidationException


@dataclass
class ApprovalOptions:
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


@dataclass
class GetOptions:
    resource: ResourceType
    name: Optional[str] = None
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
        if not self.resource:
            raise ValidationException("Resource must be specified")
        if self.owner and self.resource not in [ResourceType.DEVICE, ResourceType.FLEET]:
            raise ValidationException("Owner field is only valid for Device and Fleet kinds")
        if self.rendered and self.resource is not ResourceType.DEVICE:
            raise ValidationException("Rendered field is only valid for Device kind")
        if self.fleet_name and self.resource is not ResourceType.TEMPLATE_VERSION:
            raise ValidationException("Fleet name field is only valid for TemplateVersion kind")
        if self.summary_only:
            if self.resource is not ResourceType.DEVICE:
                raise ValidationException("Summary Only field is only valid for Device kind")
            if self.name:
                raise ValidationException("Summary Only field is not valid when fetching one Device")
        if self.summary:
            if self.resource is not ResourceType.FLEET:
                raise ValidationException("Summary field is only valid for Fleet kind")
            if not self.name:
                raise ValidationException("Summary field is only valid when fetching one Fleet")
        if self.status_filter:
            if self.resource is not ResourceType.DEVICE:
                raise ValidationException("Status filter field is only valid for Device kind")
            if self.name:
                raise ValidationException("Status filter field is not valid when fetching one Device")
        if self.label_selector and self.name:
            raise ValidationException("Label selector field is not valid when fetching one resource")
        if self.field_selector and self.name:
            raise ValidationException("Label selector field is not valid when fetching one resource")

    @property
    def request_params(self) -> dict:
        params = dict()
        if self.label_selector:
            params['label_selector'] = self.label_selector
        if self.field_selector:
            params['field_selector'] = self.field_selector
        if self.owner:
            params['owner'] = self.owner
        if self.summary:
            params['add_devices_summary'] = self.summary
        if self.summary_only:
            params['summary_only'] = self.summary_only
        if self.limit:
            params['limit'] = self.limit
        if self.continue_token:
            params['var_continue'] = self.continue_token
        if self.status_filter:
            params['status_filter'] = self.status_filter
        return params
