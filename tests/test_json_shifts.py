"""Tests for 'json_shifts.py'"""

import pandas as pd

from hockey_scraper.nhl.shifts import json_shifts


def test_get_shifts():
    """Tests to see we get something when scraping. We want it to return a dictionary"""
    assert isinstance(json_shifts.get_shifts("2016020001"), dict)
    assert isinstance(json_shifts.get_shifts("2008020768"), dict)


def test_scrape_shifts():
    """ Tests scraping the json shifts. 
        1. We either want a pandas df or None.
        2. Checks to see if the proper game scraped is the right amount of shifts
        3. Checks if right columns are included
    """
    scraped_shifts = json_shifts.scrape_game("2016020001")

    assert isinstance(scraped_shifts, pd.DataFrame)
    assert scraped_shifts.shape[0] == 850

    shift_columns = ['Game_Id', 'Period', 'Team', 'Player', 'Player_Id', 'Start', 'End', 'Duration']
    assert list(scraped_shifts.columns) == shift_columns


def test_parse_shift():
    """ Test to see that it parses a shift correctly"""
    shift = {
        "detailCode": 0, "duration": "00:46", "endTime": "04:12", "eventDescription": None, "eventDetails": None,
        "eventNumber": 327, "firstName": "Leo", "gameId": 2016020001, "hexValue": "#00205B", "lastName": "Komarov",
        "period": 2, "playerId": 8473463, "shiftNumber": 12, "startTime": "03:26", "teamAbbrev": "TOR", "teamId": 10,
        "teamName": "Toronto Maple Leafs", "typeCode": 517
    }

    parsed_shift = {'Player': 'LEO KOMAROV', 'Player_Id': 8473463, 'Period': 2, 'Team': 'TOR', 'Start': 206.0,
                    'End': 252.0, 'Duration': 46.0}

    assert json_shifts.parse_shift(shift) == parsed_shift
