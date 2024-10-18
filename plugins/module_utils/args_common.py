AUTH_ARG_SPEC = dict(
    flightctl_host=dict(type="str"),
    flightctl_username=dict(type="str", no_log=True),
    flightctl_password=dict(type="str", no_log=True),
    flightctl_token=dict(type="str", no_log=True),
    flightctl_validate_certs=dict(type="bool", default=True, aliases=['verify_ssl']),
    flightctl_request_timeout=dict(type="float", aliases=['request_timeout']),
    flightctl_config_file=dict(type="path", aliases=['config_file'])
)

STATE_ARG_SPEC = dict(
    state=dict(type="str", default="present", choices=['present', 'absent'])
)
