# Demos

This directory contains demo playbooks for creating and deleting various resources within the flightctl service.

## Running demo playbooks with a locally running flightctl instance

The following steps assume that you have a locally running flightctl cluster via the steps described in the [flightctl repo](https://github.com/flightctl/flightctl/blob/main/docs/user/getting-started.md) - e.g. `make deploy`.

1.  Begin by creating a python virtual environment with the necessary dependencies.

```
python -m venv env
source venv/bin/activate
pip install -r requirements.txt
```
2.  Install the ansible collection locally.  The '--force' argument may not always be relevant but will make sure any local changes you make show in the installed collection.
```
ansible-galaxy collection install . --force
```

3.  Run a playbook.
```
ansible-playbook demo/create.yml --extra-vars "flightctl_config_file='~/.config/flightctl/client.yaml'" --extra-vars "flightctl_validate_certs=False"
```

The `--extra-vars` allows us to pass variables into the playbooks.  In this case the create playbook is dependent on the flightctl_config_file variable pointing towards the generated client.yaml used when deploying the local flightctl services.  Default values for this are:

- OSX: "~/Library/Application\ Support/flightctl/client.yaml"
- Linux: "~/.config/flightctl/client.yaml"

Note that the `create.yml` playbook makes assertations around when certain entities are being created - this results in situations where running the create playbook twice in a row will result in a failure.  Right now the `delete.yml` playbook should be run to clean up entities generated during the `create.yml` playbook and create can then be sucessfully run once more.

### Running demo playbooks with authentication enabled

If running against flightctl services using authentication an authentication token can be passed to the modules.  Currently the easiest way to get a token is to login to flightctl via the cli.

The following steps will work for a locally deployed flightctl instance run by `AUTH=true make deploy` running keycloak.

1.  Get your password for the default keycloak demouser:
```
kubectl get secret -n flightctl-external keycloak-demouser-secret -o=jsonpath='{.data.password}' | base64 -d
```
2.  Login via the cli web flow:
```
flightctl login <your-service-address-here> --web --insecure-skip-tls-verify
```
An easy way to find your service address is to look it up in the `client.yaml` file
```
cat ~/.config/flightctl/client.yaml | grep server | awk '{print $2}'
```
3.  Enter your username (demouser) and password retrieved from step 1 in the browser window.

Note: The default access tokens provisioned have a ttl and you will need to refresh them by re-running the login step every couple of hours.


If you followed the above steps the `client.yaml` file can now be used for authentication with the flightctl services.
```
ansible-playbook demo/create.yml --extra-vars "flightctl_config_file='~/.config/flightctl/client.yaml'"
```

If you prefer the token can also be passed via an explict var.  Note that if you don't pass the flightctl_config_file other variables such as the flightctl_host will need to be set.
```
ansible-playbook demo/create.yml \
    --extra-vars "flightctl_token='your-token-here'" \
    --extra-vars "flightctl_host='your-service-address-here'" \
    --extra-vars "flightctl_validate_certs=False"
```

### Running demo playbooks with cert validation

By default the modules are configured verify the ssl connection and connections will be secure.  Local deployments by default use self-signed certs and we will need to pass some additional info to the modules to sucessfully make https requests.  Similarly to above the `client.yaml` file can be populated with cert data if the following is done:

For services deployed with auth:
```
flightctl login <other args here> --certificate-authority path/to/certs/ca.crt
```

By default relative to the main repository if a `make deploy` is done the ca.cert will be located in `bin/agent/etc/flightctl/certs/ca.crt`
```
flightctl login <other args here> --certificate-authority bin/agent/etc/flightctl/certs/ca.crt
```

Running login in this fashion will populate the `client.yaml` file with a base64 encoded crt in the `certificate-authority-data` field.  This data can be read by the modules and allow for verification if the `flightctl_config_file` argument is used.

Alternatively, a filepath to the cert file can also be directly passed via the `flightctl_ca_path` argument.
```
ansible-playbook demo/create.yml \
    --extra-vars "flightctl_host='your-service-address-here'" \
    --extra-vars "flightctl_ca_path=path/to/cert/ca.crt" \
    --extra-vars "flightctl_validate_certs=True"
```


ansible-playbook demo/create.yml \
    --extra-vars "flightctl_config_file='~/.config/flightctl/client.yaml'" \
    --extra-vars "flightctl_validate_certs=True"
