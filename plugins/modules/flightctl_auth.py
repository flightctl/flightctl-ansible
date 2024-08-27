#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, KubeVirt Team <@kubevirt>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""

module: flightctl_auth

short_description: Authenticate to Flightctl

version_added: "1.0.0"

author:
  - Alina Buzachis (@alinabuzachis)

description:
  - This module handles authenticating to Flightctl

options:
  state:
    description:
    - 
    default: present
    choices:
    - present
    - absent
    type: str
  host:
    description:
    - Provide a URL for accessing the API server.
    required: true
    type: str
  username:
    description:
    - Provide a username for authenticating with the API server.
    type: str
  password:
    description:
    - Provide a password for authenticating with the API server.
    type: str
  ca_cert:
    description:
    - "Path to a CA certificate file used to verify connection to the API server. The full certificate chain
      must be provided to avoid certificate validation errors."
    aliases: [ ssl_ca_cert ]
    type: path
  validate_certs:
    description:
    - "Whether or not to verify the API server's SSL certificates."
    type: bool
    default: true
    aliases: [ verify_ssl ]

requirements:
  - urllib3
  - requests
  - requests-oauthlib
"""

EXAMPLES = r"""#"""

RETURN = r"""#"""


import traceback
from requests.auth import HTTPBasicAuth

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib_parse import urlparse, parse_qs, urlencode
from urllib.parse import urljoin

from base64 import urlsafe_b64encode
import hashlib

# 3rd party imports
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from requests_oauthlib import OAuth2Session

    HAS_REQUESTS_OAUTH = True
except ImportError:
    HAS_REQUESTS_OAUTH = False

try:
    from urllib3.util import make_headers

    HAS_URLLIB3 = True
except ImportError:
    HAS_URLLIB3 = False

from bs4 import BeautifulSoup

K8S_AUTH_ARG_SPEC = {
    "state": {
        "default": "present",
        "choices": ["present", "absent"],
    },
    "host": {"required": True},
    "username": {},
    "password": {"no_log": True},
    "ca_cert": {"type": "path", "aliases": ["ssl_ca_cert"]},
    "validate_certs": {"type": "bool", "default": True, "aliases": ["verify_ssl"]},
}

from requests_html import HTMLSession


def get_oauthaccesstoken_objectname_from_token(token_name):
    """
    openshift convert the access token to an OAuthAccessToken resource name using the algorithm
    https://github.com/openshift/console/blob/9f352ba49f82ad693a72d0d35709961428b43b93/pkg/server/server.go#L609-L613
    """

    sha256Prefix = "sha256~"
    if token_name.startswith(sha256Prefix):
        content = token_name[len(sha256Prefix):]
    else:
        content = token_name
    b64encoded = urlsafe_b64encode(hashlib.sha256(content.encode()).digest()).rstrip(
        b"="
    )
    return sha256Prefix + b64encoded.decode("utf-8")


class FlightctlAuthModule(AnsibleModule):
    def __init__(self):
        AnsibleModule.__init__(
            self,
            argument_spec=K8S_AUTH_ARG_SPEC,
            required_if=[
                ("state", "present", ["username", "password"]),
            ],
        )

        if not HAS_REQUESTS:
            self.fail(
                "This module requires the python 'requests' package. Try `pip install requests`."
            )

        if not HAS_REQUESTS_OAUTH:
            self.fail(
                "This module requires the python 'requests-oauthlib' package. Try `pip install requests-oauthlib`."
            )

        if not HAS_URLLIB3:
            self.fail(
                "This module requires the python 'urllib3' package. Try `pip install urllib3`."
            )

    def execute_module(self):
        state = self.params.get("state")
        verify_ssl = self.params.get("validate_certs")
        ssl_ca_cert = self.params.get("ca_cert")

        self.auth_username = self.params.get("username")
        self.auth_password = self.params.get("password")
        self.con_host = self.params.get("host")

        # python-requests takes either a bool or a path to a ca file as the 'verify' param
        if verify_ssl and ssl_ca_cert:
            self.con_verify_ca = ssl_ca_cert  # path
        else:
            self.con_verify_ca = verify_ssl  # bool

        # Get needed info to access authorization APIs
        self.flightctl_discover()

        changed = False
        result = dict()
        if state == "present":
            new_api_key = self.flightctl_login()
            result = dict(
                host=self.con_host,
                validate_certs=verify_ssl,
                ca_cert=ssl_ca_cert,
                username=self.auth_username,
            )

        self.exit_json(changed=changed, new_api_key=new_api_key) #flightctl_auth=result)

    def flightctl_discover(self):
        url = urljoin(self.con_host, ".well-known/openid-configuration")
        ret = requests.get(url, verify=self.con_verify_ca)

        if ret.status_code != 200:
            self.fail_request(
                "Couldn't find Flightcl's OAuth API",
                method="GET",
                url=url,
                reason=ret.reason,
                status_code=ret.status_code,
            )

        try:
            oauth_info = ret.json()

            self.flightcl_auth_endpoint = oauth_info["authorization_endpoint"]
            self.flightcl_token_endpoint = oauth_info["token_endpoint"]
        except Exception:
            self.fail_json(
                msg="Something went wrong discovering Flightctl OAuth details.",
                exception=traceback.format_exc(),
            )

    def flightctl_login(self):
        client_id = "flightctl"
        redirect_uri = "http://localhost/callback"  # The redirect URI you registered with Keycloak

        # OAuth2 endpoints
        authorization_base_url = "https://keycloak.flightctl.edge-devices.net/realms/flightctl/protocol/openid-connect/auth"
        token_url = "https://keycloak.flightctl.edge-devices.net/realms/flightctl/protocol/openid-connect/token"

        # Create the authorization URL
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': 'openid',
        }
        session = HTMLSession()
        authorization_url = session.get(authorization_base_url, params=params).url

        # Automatically visit the authorization URL and handle redirection
        response = session.get(authorization_url)

        self.exit_json(response=response)

        # Assuming the authorization process is completed in the session (e.g., user logs in)
        # The redirect will contain the authorization code
        if response.history:
            # Extract the final URL after redirection
            final_url = response.url
            parsed_url = urlparse(final_url)
            query_params = parse_qs(parsed_url.query)
            authorization_code = query_params.get('code', [None])[0]

            if not authorization_code:
                raise Exception("Authorization code not found in the final redirected URL")

            # Exchange the authorization code for an access token
            token_data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': redirect_uri,
                'client_id': client_id,
            }
            token_response = requests.post(token_url, data=token_data, verify=False)  # adjust verify if needed

            if token_response.status_code != 200:
                raise Exception(f"Failed to obtain access token: {token_response.text}")

            token = token_response.json()
            return token['access_token']
        else:
            raise Exception("Authorization URL did not result in redirection, cannot retrieve authorization code.")

        # # Step 2: Attempt to get the login form
        # ret = os_oauth.get(
        #     authorization_url,
        #     headers={"X-Csrf-Token": state},
        #     auth=HTTPBasicAuth(self.auth_username, self.auth_password),
        #     verify=False,
        #     allow_redirects=True,
        # )

        # # Check if we received a login form (usually indicated by a 200 status code and HTML content)
        # if ret.status_code == 200 and "text/html" in ret.headers["Content-Type"]:
        #     soup = BeautifulSoup(ret.text, "html.parser")
        #     login_form = soup.find("form")
        #     if not login_form:
        #         self.fail_request(
        #             "Login form not found.",
        #             method="GET",
        #             url=authorization_url,
        #             reason="No form in the HTML page",
        #             status_code=ret.status_code,
        #             text=ret.text
        #         )
            
        #     # Extract the form's action URL
        #     form_action_url = login_form["action"]
            
        #     # Extract the form's input fields
        #     form_data = {}
        #     for input_tag in login_form.find_all("input"):
        #         name = input_tag.get("name")
        #         value = input_tag.get("value", "")
        #         form_data[name] = value
            
        #     # Update the form data with the credentials
        #     form_data.update({
        #         "username": self.auth_username,
        #         "password": self.auth_password,
        #     })

        #     # Submit the login form
        #     login_response = os_oauth.post(
        #         form_action_url,
        #         data=form_data,
        #         headers={"Content-Type": "application/x-www-form-urlencoded"},
        #         verify=False,
        #         allow_redirects=True,
        #     )

        #     # Check if login was successful (expecting a redirect)
        #     if login_response.status_code != 302:
        #         self.fail_request(
        #             "Login failed.",
        #             method="POST",
        #             url=form_action_url,
        #             reason=login_response.reason,
        #             status_code=login_response.status_code,
        #             text=login_response.text
        #         )

        #     # Process the redirect to extract the authorization code
        #     redirect_url = login_response.headers.get("Location")
        # else:
        #     # If no login form, the redirect should happen directly
        #     redirect_url = ret.headers.get("Location")

        # # Ensure the redirect URL is valid
        # if not redirect_url:
        #     self.fail_request(
        #         "No redirect location found after login attempt.",
        #         method="GET",
        #         url=authorization_url,
        #         reason="No redirect location header",
        #         status_code=ret.status_code,
        #         text=ret.text
        #     )
        
        # parsed_url = urlparse(redirect_url)
        # query_params = parse_qs(parsed_url.query)
        
        # if 'code' not in query_params:
        #     self.fail_request(
        #         "Authorization code not found in the redirect.",
        #         method="GET",
        #         url=authorization_url,
        #         reason="Authorization code missing",
        #         status_code=ret.status_code,
        #         text=ret.text
        #     )
        
        # code = query_params['code'][0]
        # qwargs = {
        #     "grant_type": "authorization_code",
        #     "code": code,
        #     "redirect_uri": authorization_url,
        # }

        # # Step 4: Exchange the authorization code for an access token
        # ret = os_oauth.post(
        #     self.flightcl_token_endpoint,
        #     headers={
        #         "Accept": "application/json",
        #         "Content-Type": "application/x-www-form-urlencoded",
        #         "Authorization": "Basic b3BlbnNoaWZ0LWNoYWxsZW5naW5nLWNsaWVudDo=",
        #     },
        #     data=urlencode(qwargs),
        #     verify=self.con_verify_ca,
        # )

        # if ret.status_code != 200:
        #     self.fail_request(
        #         "Failed to obtain an authorization token.",
        #         method="POST",
        #         url=self.flightcl_token_endpoint,
        #         reason=ret.reason,
        #         status_code=ret.status_code,
        #         text=ret.text
        #     )

        # return ret.json().get("access_token")




    #     os_oauth = OAuth2Session(client_id="flightctl")
    #     authorization_url, state = os_oauth.authorization_url(
    #         self.flightcl_auth_endpoint #, state="1", code_challenge_method="S256"
    #     )
    #     auth_headers = make_headers(
    #         basic_auth="{0}:{1}".format(self.auth_username, self.auth_password)
    #     )

    #     # Request authorization code using basic auth credentials
    #     ret = os_oauth.get(
    #         authorization_url,
    #         headers={
    #             "X-Csrf-Token": state,
    #             "authorization": auth_headers.get("authorization"),
    #         },
    #         verify=False, #self.con_verify_ca,
    #         allow_redirects=True,
    #     )

    #     if ret.status_code != 302:
    #         self.fail_request(
    #             "Authorization failed.",
    #             method="GET",
    #             url=authorization_url,
    #             reason=ret.reason,
    #             status_code=ret.status_code,
    #             text=ret.text
    #         )

    #     # In here we have `code` and `state`, I think `code` is the important one
    #     qwargs = {}
    #     for k, v in parse_qs(urlparse(ret.headers["Location"]).query).items():
    #         qwargs[k] = v[0]
    #     qwargs["grant_type"] = "authorization_code"

    #     # Using authorization code given to us in the Location header of the previous request, request a token
    #     ret = os_oauth.post(
    #         self.openshift_token_endpoint,
    #         headers={
    #             "Accept": "application/json",
    #             "Content-Type": "application/x-www-form-urlencoded",
    #             # This is just base64 encoded 'openshift-challenging-client:'
    #             "Authorization": "Basic b3BlbnNoaWZ0LWNoYWxsZW5naW5nLWNsaWVudDo=",
    #         },
    #         data=urlencode(qwargs),
    #         verify=self.con_verify_ca,
    #     )

    #     if ret.status_code != 200:
    #         self.fail_request(
    #             "Failed to obtain an authorization token.",
    #             method="POST",
    #             url=self.openshift_token_endpoint,
    #             reason=ret.reason,
    #             status_code=ret.status_code,
    #         )

    #     return ret.json()["access_token"]

    def fail(self, msg=None):
        self.fail_json(msg=msg)

    def fail_request(self, msg, **kwargs):
        req_info = {}
        for k, v in kwargs.items():
            req_info["req_" + k] = v
        self.fail_json(msg=msg, **req_info)


def main():
    module = FlightctlAuthModule()
    try:
        module.execute_module()
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())

if __name__ == "__main__":
    main()