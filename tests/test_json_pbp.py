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
        "players": [{
          "player": {
            "id": 8468575,
            "fullName": "Dominic Moore",
            "link": "/api/v1/people/8468575"
          },
          "playerType": "Scorer",
          "seasonTotal": 3
        }, {
          "player": {
            "id": 8470619,
            "fullName": "Brian Boyle",
            "link": "/api/v1/people/8470619"
          },
          "playerType": "Assist",
          "seasonTotal": 4
        }, {
          "player": {
            "id": 8474151,
            "fullName": "Ryan McDonagh",
            "link": "/api/v1/people/8474151"
          },
          "playerType": "Assist",
          "seasonTotal": 10
        }, {
          "player": {
            "id": 8474682,
            "fullName": "Dustin Tokarski",
            "link": "/api/v1/people/8474682"
          },
          "playerType": "Goalie"
        } ],
        "result": {
          "event": "Goal",
          "eventCode": "NYR294",
          "eventTypeId": "GOAL",
          "description": "Dominic Moore (3) Snap Shot, assists: Brian Boyle (4), Ryan McDonagh (10)",
          "secondaryType": "Snap Shot",
          "strength": {
            "code": "EVEN",
            "name": "Even"
          },
          "gameWinningGoal": True,
          "emptyNet": False
        },
        "about": {
          "eventIdx": 180,
          "eventId": 294,
          "period": 2,
          "periodType": "REGULAR",
          "ordinalNum": "2nd",
          "periodTime": "18:07",
          "periodTimeRemaining": "01:53",
          "dateTime": "2014-05-30T01:36:12Z",
          "goals": {
            "away": 0,
            "home": 1
          }
        },
        "coordinates": {
          "x": 77.0,
          "y": 5.0
        },
        "team": {
          "id": 3,
          "name": "New York Rangers",
          "link": "/api/v1/teams/3",
          "triCode": "NYR"
        }
    }

    parsed_event = {
        'event_id': 180, 'period': 2, 'event': 'GOAL', 'seconds_elapsed': 1087.0, 'p1_name': 'DOMINIC MOORE',
        'p1_ID': 8468575, 'p2_name': 'BRIAN BOYLE', 'p2_ID': 8470619, 'p3_name': 'RYAN MCDONAGH', 'p3_ID': 8474151,
        'xC': 77.0, 'yC': 5.0
    }

    assert json_pbp.parse_event(event) == parsed_event
