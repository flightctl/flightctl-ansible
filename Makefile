TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-integration:
	ansible-test integration --diff --no-temp-workdir --color --python $(PYTHON_VERSION) -v $(?TEST_ARGS)

test-sanity:
	ansible-test sanity plugins/ --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

generate-api-client:
	npx @openapitools/openapi-generator-cli generate \
	-g python \
	-i ./api/v1alpha1/openapi.yml \
	-o ./lib/flightctl_api_client \
	--global-property=apiDocs=false,modelDocs=false,apiTests=false,modelTests=false \
	--additional-properties=generateSourceCodeOnly=true
