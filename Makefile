TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

test-integration:
	ansible-test integration --diff --no-temp-workdir --color --python $(PYTHON_VERSION) -v $(?TEST_ARGS)

test-sanity:
	ansible-test sanity --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)

generate-api-client:
	npx @openapitools/openapi-generator-cli generate \
	-g python \
	-i ./api/v1alpha1/openapi.yml \
	-o ./lib/flightctl_api_client \
	--global-property=apiDocs=false,modelDocs=false,apiTests=false,modelTests=false \
	--additional-properties=generateSourceCodeOnly=true

generate-sanity-ignore-file:
	rm tests/sanity/ignore-2.16.txt
	cp tests/sanity/ignore-base.txt tests/sanity/ignore-2.16.txt
	find lib/flightctl_api_client/openapi_client -type f -name "*.py" | \
	while read filepath; do \
		echo "$$filepath pep8!skip" >> tests/sanity/ignore-2.16.txt; \
		echo "$$filepath pylint!skip" >> tests/sanity/ignore-2.16.txt; \
	done
