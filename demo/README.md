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
ansible-playbook demo/create.yml --extra-vars "flightctl_config_file='~/.flightctl/client.yaml'"
```

The `--extra-vars` allows us to pass variables into the playbooks.  In this case the create playbook is dependent on the flightctl_config_file variable pointing towards the generated client.yaml used when deploying the local flightctl services.

Note that the `create.yml` playbook makes assertations around when certain entities are being created - this results in situations where running the create playbook twice in a row will result in a failure.  Right now the `delete.yml` playbook should be run to clean up entities generated during the `create.yml` playbook and create can then be sucessfully run once more.
