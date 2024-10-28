TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-integration:
	ansible-test integration --diff --no-temp-workdir --color --python $(PYTHON_VERSION) -v $(?TEST_ARGS)

test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

generate-api-client:
	openapi-python-client generate \
		--config client-gen-config.yaml \
		--output-path plugins/module_utils/flightctl_api_client \
		--meta none \
		--path api/v1alpha1/openapi.yml \
		--overwrite
