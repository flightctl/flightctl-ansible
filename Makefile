TEST_ARGS ?= ""
PYTHON_VERSION ?= `python -c 'import platform; print(".".join(platform.python_version_tuple()[0:2]))'`

test-unit:
	ansible-test units --docker -v --color --python $(PYTHON_VERSION) $(?TEST_ARGS)
