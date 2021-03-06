""" Tests for 'shared.py' """

import os
import shutil
import pytest

from hockey_scraper.utils import shared, config


@pytest.fixture
def file_info():
    return {
        "url": 'http://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(2017020001),
        "name": str(2017020001),
        "type": "json_pbp",
        "season": 2017,
    }


def test_check_data_format():
    """ Test if it recognized the correct formats allowed"""
    # These both are fine
    shared.check_data_format("Csv")
    shared.check_data_format("pandaS")

    # Should raise an exception
    with pytest.raises(ValueError):
        shared.check_data_format("txt")


def test_check_valid_dates():
    """ Test if given valid date range"""
    shared.check_valid_dates("2017-10-01", "2018-01-05")

    with pytest.raises(ValueError):
        shared.check_valid_dates("2017-12-01", "2017-11-30")


def test_convert_to_seconds():
    """ Tests if it correctly converts minutes remaining to seconds elapsed"""
    assert shared.convert_to_seconds("8:33") == 513
    assert shared.convert_to_seconds("-16:0-") == "1200"


def test_get_season():
    """ Tests that this function returns the correct season for a given date"""
    assert shared.get_season("2017-10-01") == 2017
    assert shared.get_season("2016-06-01") == 2015
    assert shared.get_season("2020-08-29") == 2019
    assert shared.get_season("2020-10-03") == 2019
    assert shared.get_season("2020-11-15") == 2020


def test_scrape_page(file_info):
    """ Test scraping from the source is good"""
    file = shared.scrape_page(file_info['url'])

    assert type(file) == str
    assert len(file) > 0


def test_get_file(file_info):
    """ Test getting the file...it's either scraped or loaded from a file """
    original_path = os.getcwd()

    # When there is either no directory specified or it doesn't exist
    file = shared.get_file(file_info)
    assert type(file) == str
    assert len(file) > 0
    assert original_path == os.getcwd()

    # When the directory exists
    # Here I just use the directory of this file to make things easy
    shared.add_dir(os.path.dirname(os.path.realpath(__file__)))
    file = shared.get_file(file_info)
    assert type(file) == str
    assert len(file) > 0
    assert original_path == os.getcwd()

    # Some cleanup....remove stuff created from the file directory and move back
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    shutil.rmtree("docs")
    shutil.rmtree("csvs")
    os.chdir(original_path)


def test_add_dir():
    """ Test if this function correctly tells if a directory exists on the machine"""

    # Check when it does exist (will always be good for this file)
    user_dir = os.path.dirname(os.path.realpath(__file__))
    shared.add_dir(user_dir)
    assert config.DOCS_DIR is not None

    # Checks when it doesn't exist
    user_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hopefully_this_path_doesnt_exist")
    shared.add_dir(user_dir)
    assert config.DOCS_DIR is False