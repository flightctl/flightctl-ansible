TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

unit-test:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

integration-test: write-integration-config
	ansible-test integration --docker --diff --color --python $(PYTHON_VERSION) -v $(?TEST_ARGS)

# Running an integration test for the connection plugin is possible, but currently marked as
# unsupported in ansible-test and thus does not run in CI.
#
# To run the integration test locally, requirements are a running flightctl server as well as an
# onboarded and connected device.  The ansible_flightctl_device_name in the test must be manually set
# to the name of the device you want to test against.
integration-test-connection: write-integration-config
	ansible-test integration connection_flightctl_console \
		--docker --diff --color --python $(PYTHON_VERSION) --allow-unsupported -v

sanity-test:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

write-integration-config:
	@token="$$(grep '^  token:' ~/.config/flightctl/client.yaml | awk '{print $$2}')"; \
	service_addr="$$(awk '/^service:/,/^  server:/' ~/.config/flightctl/client.yaml | grep 'server:' | awk '{print $$2}')"; \
	echo "flightctl_token: $$token" > ./tests/integration/integration_config.yml; \
	echo "flightctl_host: $$service_addr" >> ./tests/integration/integration_config.yml;
