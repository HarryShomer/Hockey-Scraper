import pytest


def pytest_addoption(parser):
    parser.addoption('--live', action='store_true', help='Run live tests')


def pytest_runtest_setup(item):
    if item.get_marker('live') and not item.config.getoption('--live'):
        pytest.skip('Skipping live test')
