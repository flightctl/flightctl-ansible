TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-integration:
	ansible-test integration --diff --no-temp-workdir --color --python $(PYTHON_VERSION) -v $(?TEST_ARGS)

test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

generate-api-client: build-client move-client-files

build-client:
	npx @openapitools/openapi-generator-cli generate \
	-g python \
	-i ./api/v1alpha1/openapi.yml \
	-o ./tmp-client \
	--additional-properties=generateSourceCodeOnly=true \
	--global-property=apiDocs=false,modelDocs=false,apiTests=false,modelTests=false \
	-c ./openapiconfig.json

# TODO add explanation for this shenanigans
move-client-files:
	mv ./tmp-client/ansible_collections/flightctl/edge/plugins/module_utils/api_client ./plugins/module_utils
	mv ./tmp-client/ansible_collections/flightctl/edge/plugins/module_utils/*README.md ./plugins/module_utils/api_client
	rm -rf ./tmp-client
