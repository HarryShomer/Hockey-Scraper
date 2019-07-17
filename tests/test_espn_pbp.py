""" Tests for 'espn_pbp.py' """

import pandas as pd
import pytest

from hockey_scraper.nhl.pbp import espn_pbp


@pytest.fixture
def game_date():
    return '2015-10-24'


@pytest.fixture
def teams():
    return {'Home': 'PHI', 'Away': 'NYR'}


@pytest.fixture
def game_response(game_date, teams):
    """ Page for that game"""
    return espn_pbp.get_espn_game(game_date, teams['Home'], teams['Away'])


@pytest.fixture
def date_response(game_date):
    """ Page that details all the games that day"""
    return espn_pbp.get_espn_date(game_date)


def test_get_teams(date_response):
    """ Check to make sure we get a list of both teams for every game that day"""

    # Games for that date
    date_games = [['ANA', 'MIN'], ['N.J', 'BUF'], ['TOR', 'MTL'], ['PHX', 'OTT'], ['NYR', 'PHI'], ['NYI', 'STL'],
                  ['PIT', 'NSH'], ['FLA', 'DAL'], ['T.B', 'CHI'], ['CBJ', 'COL'], ['DET', 'VAN'], ['CAR', 'S.J']]

    assert espn_pbp.get_teams(date_response) == date_games


def test_get_game_ids(date_response):
    """ Check to see that all the espn game id's for that day are correct"""
    game_ids = ['400814970', '400814971', '400814972', '400814973', '400814974', '400814975', '400814976',
                '400814977', '400814978', '400814979', '400814980', '400814981']

    assert espn_pbp.get_game_ids(date_response) == game_ids


def test_get_espn_game_id(game_date, teams):
    """ 
    Test to see for a given game (identified by the game_id and both teams) it return the correct game_id number
    for the Espn api.
    """
    assert espn_pbp.get_espn_game_id(game_date, teams['Home'], teams['Away']) == '400814974'


def test_get_espn_game(game_response):
    """ Test to see if we get anything back whn requesting a game. Should be a non-empty string"""
    assert type(game_response) == str
    assert len(game_response) > 0


def test_parse_event():
    """ Checks to see that it correctly parses a game event"""
    event = "-35~12~505~4:48~2~3506~5767~5833~Power Play Goal Scored by Derick Brassard(Slapshot 56 ft)assisted by " \
            "Kevin Hayes and Chris Kreider~0~2~2~0~702~13~801~901~2~3~4"
    parsed_event = {"xC": -35, "yC": 12, "time_elapsed": 288, 'period': '2', 'event': "GOAL"}

    assert espn_pbp.parse_event(event) == parsed_event


def test_parse_espn(game_response):
    """ Checks if the espn game response is parsed correctly. Specifically: 
        1. Is a DataFrame?
        2. Contains the correct amount of events?
        3. Contains the correct columns?
    """
    scraped_game = espn_pbp.parse_espn(game_response)
    espn_columns = ['period', 'time_elapsed', 'event', 'xC', 'yC']

    assert isinstance(scraped_game, pd.DataFrame)
    assert scraped_game.shape[0] == 379
    assert list(scraped_game.columns) == espn_columns
