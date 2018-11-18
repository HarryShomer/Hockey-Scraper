""" Tests for 'scrape_functions.py' """

import pytest
import pandas as pd
from hockey_scraper import scrape_functions
import hockey_scraper.shared as shared


def test_check_data_format():
    """ Test if it recognized the correct formats allowed"""
    # These both are fine
    scrape_functions.check_data_format("Csv")
    scrape_functions.check_data_format("pandaS")

    # Should raise an exception
    with pytest.raises(shared.HaltException):
        scrape_functions.check_data_format("txt")


def test_check_valid_dates():
    """ Test if given valid date range"""
    scrape_functions.check_valid_dates("2017-10-01", "2018-01-05")

    with pytest.raises(shared.HaltException):
        scrape_functions.check_valid_dates("2017-12-01", "2017-11-30")


def test_scrape_list_of_games():
    """ Tests that it correctly scraped a given list of [game_id, date]"""
    games = [
        {'game_id': '2017020001', 'date': '2017-10-04', 'status': 'Final'},
        {'game_id': '2017020746', 'date': '2018-01-25', 'status': 'Final'},
        {'game_id': '2017020450', 'date': '2017-12-09', 'status': 'Final'},
        {'game_id': '2017030311', 'date': '2018-05-11', 'status': 'Final'}
    ]

    # First try without shifts
    pbp, shifts = scrape_functions.scrape_list_of_games(games[:2], False)
    assert isinstance(pbp, pd.DataFrame)
    assert shifts is None
    assert pbp.shape[0] == 614

    # Second we try with shifts
    pbp, shifts = scrape_functions.scrape_list_of_games(games[2:], True)
    assert isinstance(pbp, pd.DataFrame)
    assert isinstance(shifts, pd.DataFrame)
    assert pbp.shape[0] == 602
    assert shifts.shape[0] == 1531

    # Third we feed it a bullshit game_id and see what happens
    pbp, shifts = scrape_functions.scrape_list_of_games([{"game_id": "2016022000", "date": "", "status": ""}], True)
    assert pbp is None
    assert shifts is None
