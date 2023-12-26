"""Tests for 'json_pbp.py'"""

import pandas as pd

from hockey_scraper.nhl.pbp import json_pbp


def test_get_pbp():
    """Tests to see we get something when scraping. We want it to return a dictionary"""
    assert isinstance(json_pbp.get_pbp("2016020001"), dict)
    assert isinstance(json_pbp.get_pbp("2008020768"), dict)


def test_get_teams():
    """Tests how extracting home and away teams from json"""
    assert json_pbp.get_teams(json_pbp.get_pbp("2014020001")) == {"Home": 'TOR', "Away": 'MTL'}


def test_parse_json():
    """ Tests how the pbp for one game is stored
        1. We want it to return a pandas DataFrame
        2. Checks to see if the proper game scraped is the right amount of events
        3. Checks if the right columns are included
    """
    scraped_game = json_pbp.scrape_game("2016020001")
    pbp_columns = ['period', 'event', 'seconds_elapsed', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID',
                   'xC', 'yC']

    assert isinstance(scraped_game, pd.DataFrame)
    assert scraped_game.shape[0] == 349
    assert list(scraped_game.columns) == pbp_columns


def test_parse_event():
    """ Test to see that it parses an event correctly"""

    event = {
            "eventId": 201,
            "period": 1,
            "periodDescriptor": {
                "number": 1,
                "periodType": "REG"
            },
            "timeInPeriod": "00:32",
            "timeRemaining": "19:28",
            "situationCode": "1551",
            "homeTeamDefendingSide": "right",
            "typeCode": 505,
            "typeDescKey": "goal",
            "sortOrder": 20,
            "details": {
                "xCoord": -84,
                "yCoord": 6,
                "zoneCode": "O",
                "shotType": "wrist",
                "scoringPlayerId": 8478864,
                "assist1PlayerId": 8482122,
                "assist2PlayerId": 8475692,
                "eventOwnerTeamId": 30,
                "goalieInNetId": 8481020,
                "awayScore": 0,
                "homeScore": 1
            }
        }

    parsed_event = {
        'event_id': 201, 'period': 1, 'event': 'GOAL', 'seconds_elapsed': 32.0, 'p1_name': '',
        'p1_ID': 8478864, 'p2_name': '', 'p2_ID': 8482122, 'p3_name': '', 'p3_ID': 8475692,
        'xC': -84.0, 'yC': 6.0
    }

    assert json_pbp.parse_event(event) == parsed_event
