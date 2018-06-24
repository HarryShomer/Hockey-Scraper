"""Tests for 'json_schedule.py'"""
from hockey_scraper import json_schedule


def test_get_schedule():
    """Tests to see we get something when scraping. We want it to return a dictionary"""
    assert isinstance(json_schedule.get_schedule("2018-03-28", "2018-07-01"), dict)
    assert isinstance(json_schedule.get_schedule("2017-09-01", "2018-09-15"), dict)


def test_scrape_schedule():
    """Test to see if successfully get the correct number of games between two dates"""
    assert len(json_schedule.scrape_schedule("2017-08-01", "2017-09-01")) == 0
    assert len(json_schedule.scrape_schedule("2017-09-01", "2017-11-15")) == 277
    assert len(json_schedule.scrape_schedule("2017-09-01", "2017-11-15", preseason="True")) == 385


def test_get_dates():
    """Test to see that it returns the correct dates for given game id's"""
    assert json_schedule.get_dates([2015010002])[0] == [2015010002, "2015-09-20"]
    assert json_schedule.get_dates([2017020275])[0] == [2017020275, "2017-11-15"]
    assert json_schedule.get_dates([2014030416])[0] == [2014030416, "2015-06-15"]



