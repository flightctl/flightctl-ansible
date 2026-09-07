from pathlib import Path

import yaml


def test_v1_3_certificate_management_target_excludes_unsupported_csr_scenarios():
    """Flight Control v1.3 rejects the old admin-token CSR scenarios."""
    target = Path(__file__).parents[1] / "integration/targets/flightctl_certificate_management/tasks/main.yml"

    with target.open() as file:
        tasks = yaml.safe_load(file)

    assert tasks == [
        {"include_tasks": "enrollment-approval.yml"},
        {"include_tasks": "enrollment-denial.yml"},
    ]
