"""Tests for 'json_schedule.py'"""
import datetime

from hockey_scraper.nhl import json_schedule


def test_get_schedule():
    """Tests to see we get something when scraping. We want it to return a dictionary"""
    assert isinstance(json_schedule.get_schedule("2018-03-28", "2018-07-01"), dict)


def test_scrape_schedule():
    """Test to see if successfully get the correct number of games between two dates"""
    assert len(json_schedule.scrape_schedule("2017-08-01", "2017-09-01")) == 0
    assert len(json_schedule.scrape_schedule("2017-09-01", "2017-11-15")) == 277
    assert len(json_schedule.scrape_schedule("2017-09-01", "2017-11-15", preseason="True")) == 385


def test_get_dates():
    """Test to see that it returns the correct dates for given game id's"""
    assert json_schedule.get_dates([2015010002])[0] == {'game_id': 2015010002, 'date': '2015-09-20', 
                                                        'start_time': datetime.datetime(2015, 9, 20, 20, 30), 
                                                        'venue': 'Bridgestone Arena', 'home_team': 'NSH', 
                                                        'away_team': 'FLA', 'home_score': 5, 'away_score': 2, 
                                                        'status': 'Final'}
    assert json_schedule.get_dates([2017020275])[0] == {'game_id': 2017020275, 'date': '2017-11-15', 
                                                        'start_time': datetime.datetime(2017, 11, 16, 0, 30), 
                                                        'venue': 'Little Caesars Arena', 'home_team': 'DET', 
                                                        'away_team': 'CGY', 'home_score': 8, 'away_score': 2, 
                                                        'status': 'Final'}
    assert json_schedule.get_dates([2014030416])[0] == {'game_id': 2014030416, 'date': '2015-06-15', 
                                                        'start_time': datetime.datetime(2015, 6, 16, 0, 0), 
                                                        'venue': 'United Center', 'home_team': 'CHI', 
                                                        'away_team': 'T.B', 'home_score': 2, 'away_score': 0, 
                                                        'status': 'Final'}


def test_chunk_schedule_calls():
    """
    Test that we appropriately chunk calls in a range. Do so by by checking # of days in each chunk.

    chunk_size = 30

    Note: Won't always go to total days in interval as some days dont' have games
    """
    # 1 day
    x = json_schedule.chunk_schedule_calls('2019-10-10', '2019-10-10')
    assert [len(chunk) for chunk in x] == [1]

    # > 50
    x = json_schedule.chunk_schedule_calls('2018-10-10', '2019-04-10')
    assert [len(chunk) for chunk in x] == [29, 29, 27, 27, 30, 29, 1]

    # 1 < x < 50
    x = json_schedule.chunk_schedule_calls('2018-10-10', '2018-11-15')
    assert [len(chunk) for chunk in x] == [29, 7]





