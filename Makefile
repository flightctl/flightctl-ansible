TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-integration:
	ansible-test integration --diff --no-temp-workdir --color --python $(PYTHON_VERSION) -v $(?TEST_ARGS)

test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

generate-api-client: build-client replace-client-files

build-client:
	npx @openapitools/openapi-generator-cli generate \
	-g python \
	-i ./api/v1alpha1/openapi.yml \
	-o ./tmp-client \
	--additional-properties=generateSourceCodeOnly=true \
	--global-property=apiDocs=false,modelDocs=false,apiTests=false,modelTests=false \
	-c ./openapiconfig.json

# The client is generated in a tmp directory with this file structure so that it will have
# absolute import paths that work inside the ansible collection.
#
# If this GH issue is ever completed this could be changed https://github.com/OpenAPITools/openapi-generator/issues/1302,
# or if the generated client code would be moved to a separate repository and imported as a single python dependency.
replace-client-files:
	rm -rf ./plugins/module_utils/api_client
	mv ./tmp-client/ansible_collections/flightctl/edge/plugins/module_utils/api_client ./plugins/module_utils/api_client
	mv ./tmp-client/ansible_collections/flightctl/edge/plugins/module_utils/*README.md ./plugins/module_utils/api_client
	rm -rf ./tmp-client
