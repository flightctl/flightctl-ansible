def pytest_configure(config):
    config.option.asyncio_mode = "auto"
    # Setting asyncio_default_fixture_loop_scope prevents many
    # warning logs in the test runner
    config._inicache["asyncio_default_fixture_loop_scope"] = "function"
