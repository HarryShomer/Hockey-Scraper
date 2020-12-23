""" Tests for 'game_scraper.py' """

import pandas as pd
import pytest

from hockey_scraper.nhl import game_scraper, playing_roster
from hockey_scraper.nhl.pbp import json_pbp


@pytest.fixture
def players():
    return {'Home':
               {'NOAH HANIFIN': {'id': 8478396, 'number': '5', 'last_name': 'HANIFIN'},
                'KLAS DAHLBECK': {'id': 8476403, 'number': '6', 'last_name': 'DAHLBECK'},
                'DEREK RYAN': {'id': 8478585, 'number': '7', 'last_name': 'RYAN'},
                'JORDAN STAAL': {'id': 8473533, 'number': '11', 'last_name': 'STAAL'},
                'JUSTIN WILLIAMS': {'id': 8468508, 'number': '14', 'last_name': 'WILLIAMS'},
                'SEBASTIAN AHO': {'id': 8478427, 'number': '20', 'last_name': 'AHO'},
                'LEE STEMPNIAK': {'id': 8470740, 'number': '21', 'last_name': 'STEMPNIAK'},
                'BRETT PESCE': {'id': 8477488, 'number': '22', 'last_name': 'PESCE'},
                'BROCK MCGINN': {'id': 8476934, 'number': '23', 'last_name': 'MCGINN'},
                'JUSTIN FAULK': {'id': 8475753, 'number': '27', 'last_name': 'FAULK'},
                'ELIAS LINDHOLM': {'id': 8477496, 'number': '28', 'last_name': 'LINDHOLM'},
                'PHILLIP DI GIUSEPPE': {'id': 8476858, 'number': '34', 'last_name': 'DI GIUSEPPE'},
                'JOAKIM NORDSTROM': {'id': 8475807, 'number': '42', 'last_name': 'NORDSTROM'},
                'VICTOR RASK': {'id': 8476437, 'number': '49', 'last_name': 'RASK'},
                'JEFF SKINNER': {'id': 8475784, 'number': '53', 'last_name': 'SKINNER'},
                'TREVOR VAN RIEMSDYK': {'id': 8477845, 'number': '57', 'last_name': 'VAN RIEMSDYK'},
                'JACCOB SLAVIN': {'id': 8476958, 'number': '74', 'last_name': 'SLAVIN'},
                'TEUVO TERAVAINEN': {'id': 8476882, 'number': '86', 'last_name': 'TERAVAINEN'},
                'CAM WARD': {'id': 8470320, 'number': '30', 'last_name': 'WARD'},
                'HAYDN FLEURY': {'id': 8477938, 'number': '4', 'last_name': 'FLEURY'},
                'PATRICK BROWN': {'id': 8477887, 'number': '36', 'last_name': 'BROWN'}
                },
            'Away':
                {'NICK LEDDY': {'id': 8475181, 'number': '2', 'last_name': 'LEDDY'},
                 'RYAN PULOCK': {'id': 8477506, 'number': '6', 'last_name': 'PULOCK'},
                 'JORDAN EBERLE': {'id': 8474586, 'number': '7', 'last_name': 'EBERLE'},
                 'JOSH BAILEY': {'id': 8474573, 'number': '12', 'last_name': 'BAILEY'},
                 'MATHEW BARZAL': {'id': 8478445, 'number': '13', 'last_name': 'BARZAL'},
                 'THOMAS HICKEY': {'id': 8474066, 'number': '14', 'last_name': 'HICKEY'},
                 'CAL CLUTTERBUCK': {'id': 8473504, 'number': '15', 'last_name': 'CLUTTERBUCK'},
                 'ANDREW LADD': {'id': 8471217, 'number': '16', 'last_name': 'LADD'},
                 'ANDERS LEE': {'id': 8475314, 'number': '27', 'last_name': 'LEE'},
                 'SEBASTIAN AHO': {'id': 8480222, 'number': '28', 'last_name': 'AHO'},
                 'BROCK NELSON': {'id': 8475754, 'number': '29', 'last_name': 'NELSON'},
                 'ADAM PELECH': {'id': 8476917, 'number': '50', 'last_name': 'PELECH'},
                 'ROSS JOHNSTON': {'id': 8477527, 'number': '52', 'last_name': 'JOHNSTON'},
                 'CASEY CIZIKAS': {'id': 8475231, 'number': '53', 'last_name': 'CIZIKAS'},
                 'JOHNNY BOYCHUK': {'id': 8470187, 'number': '55', 'last_name': 'BOYCHUK'},
                 'TANNER FRITZ': {'id': 8479206, 'number': '56', 'last_name': 'FRITZ'},
                 'ANTHONY BEAUVILLIER': {'id': 8478463, 'number': '72', 'last_name': 'BEAUVILLIER'},
                 'JOHN TAVARES': {'id': 8475166, 'number': '91', 'last_name': 'TAVARES'},
                 'THOMAS GREISS': {'id': 8471306, 'number': '1', 'last_name': 'GREISS'},
                 'DENNIS SEIDENBERG': {'id': 8469619, 'number': '4', 'last_name': 'SEIDENBERG'},
                 'ALAN QUINE': {'id': 8476409, 'number': '10', 'last_name': 'QUINE'},
                 'JASON CHIMERA': {'id': 8466251, 'number': '25', 'last_name': 'CHIMERA'}
                 }
            }


@pytest.fixture
def pbp_columns():
    return ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
            'Ev_Zone', 'Type', 'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
            'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
            'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
            'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
            'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
            'homePlayer6_id', 'Away_Players', 'Home_Players', 'Away_Score', 'Home_Score', 'Away_Goalie',
            'Away_Goalie_Id', 'Home_Goalie', 'Home_Goalie_Id', 'xC', 'yC', 'Home_Coach', 'Away_Coach'
            ]


@pytest.fixture
def shifts_columns():
    return ['Game_Id', 'Period', 'Team', 'Player', 'Player_Id', 'Start', 'End', 'Duration', 'Date']


def test_scrape_game(pbp_columns, shifts_columns):
    """ Tests if scrape pbp and shifts for game correctly with and without shifts.
        Check:
            1. Returns either a DataFrame or None (for shifts when False)
            2. The number of rows is correct
            3. The columns are correct
     """

    # 1. Try first without shifts
    pbp, shifts = game_scraper.scrape_game("2016020475", "2016-12-18", False)
    assert isinstance(pbp, pd.DataFrame)
    assert shifts is None
    assert pbp.shape[0] == 326
    assert list(pbp.columns) == pbp_columns

    # 2. Try with shifts
    pbp, shifts = game_scraper.scrape_game("2007020222", "2007-11-08", True)
    assert isinstance(pbp, pd.DataFrame)
    assert isinstance(shifts, pd.DataFrame)
    assert pbp.shape[0] == 248
    assert shifts.shape[0] == 726
    assert list(pbp.columns) == pbp_columns
    assert list(shifts.columns) == shifts_columns


def test_combine_players_lists(players):
    """ Check that it combines the list of players from the json pbp and the html roster correctly """
    game_id = "2017020891"
    json_players = game_scraper.get_players_json(json_pbp.get_pbp(game_id))
    roster = playing_roster.scrape_roster(game_id)['players']

    assert players == game_scraper.combine_players_lists(json_players, roster, game_id)
