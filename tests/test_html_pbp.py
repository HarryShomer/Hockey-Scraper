""" Tests for 'html_pbp.py' """

import pandas as pd
import pytest

from hockey_scraper.nhl.pbp import html_pbp


# TODO: Fill out the rest of the test here and in the file (the important ones there)


@pytest.fixture
def game_id():
    return "2017020516"


@pytest.fixture
def cleaned_html(game_id):
    return html_pbp.clean_html_pbp(html_pbp.get_pbp(game_id))


@pytest.fixture
def pbp_cols():
    return ['Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength', 'Ev_Zone', 'Type',
            'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name',
            'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id',
            'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id',
            'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3', 'homePlayer3_id',
            'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6', 'homePlayer6_id',
            'Away_Goalie', 'Away_Goalie_Id', 'Home_Goalie', 'Home_Goalie_Id', 'Away_Players', 'Home_Players',
            'Away_Score', 'Home_Score'
            ]


@pytest.fixture
def event():
    return ['112', '1', 'EV', '15:59', 'PENL', 'TOR #25 VAN RIEMSDYK\xa0Slashing(2 min), Off. Zone Drawn By: CAR #49 RASK',
            [['VICTOR RASK', '49', 'C'], ['JEFF SKINNER', '53', 'C'], ['TEUVO TERAVAINEN', '86', 'L'],
             ['NOAH HANIFIN', '5', 'D'], ['BRETT PESCE', '22', 'D'], ['SCOTT DARLING', '33', 'G']],
            [['MITCHELL MARNER', '16', 'C'], ['TYLER BOZAK', '42', 'C'], ['JAMES VAN RIEMSDYK', '25', 'L'],
             ['ROMAN POLAK', '46', 'D'], ['JAKE GARDINER', '51', 'D'], ['FREDERIK ANDERSEN', '31', 'G']]
            ]

@pytest.fixture
def players():
    return {'Home':
                {'RON HAINSEY': {'id': 8468493, 'number': '2', 'last_name': 'HAINSEY'},
                 'CONNOR CARRICK': {'id': 8476941, 'number': '8', 'last_name': 'CARRICK'},
                 'ZACH HYMAN': {'id': 8475786, 'number': '11', 'last_name': 'HYMAN'},
                 'PATRICK MARLEAU': {'id': 8466139, 'number': '12', 'last_name': 'MARLEAU'},
                 'MATT MARTIN': {'id': 8474709, 'number': '15', 'last_name': 'MARTIN'},
                 'MITCHELL MARNER': {'id': 8478483, 'number': '16', 'last_name': 'MARNER'},
                 'DOMINIC MOORE': {'id': 8468575, 'number': '20', 'last_name': 'MOORE'},
                 'KASPERI KAPANEN': {'id': 8477953, 'number': '24', 'last_name': 'KAPANEN'},
                 'JAMES VAN RIEMSDYK': {'id': 8474037, 'number': '25', 'last_name': 'VAN RIEMSDYK'},
                 'CONNOR BROWN': {'id': 8477015, 'number': '28', 'last_name': 'BROWN'},
                 'WILLIAM NYLANDER': {'id': 8477939, 'number': '29', 'last_name': 'NYLANDER'},
                 'TYLER BOZAK': {'id': 8475098, 'number': '42', 'last_name': 'BOZAK'},
                 'NAZEM KADRI': {'id': 8475172, 'number': '43', 'last_name': 'KADRI'},
                 'MORGAN RIELLY': {'id': 8476853, 'number': '44', 'last_name': 'RIELLY'},
                 'ROMAN POLAK': {'id': 8471392, 'number': '46', 'last_name': 'POLAK'},
                 'LEO KOMAROV': {'id': 8473463, 'number': '47', 'last_name': 'KOMAROV'},
                 'JAKE GARDINER': {'id': 8474581, 'number': '51', 'last_name': 'GARDINER'},
                 'ANDREAS BORGMAN': {'id': 8480158, 'number': '55', 'last_name': 'BORGMAN'},
                 'FREDERIK ANDERSEN': {'id': 8475883, 'number': '31', 'last_name': 'ANDERSEN'},
                 'JOSH LEIVO': {'id': 8476410, 'number': '32', 'last_name': 'LEIVO'},
                 'AUSTON MATTHEWS': {'id': 8479318, 'number': '34', 'last_name': 'MATTHEWS'},
                 'MARTIN MARINCIN': {'id': 8475716, 'number': '52', 'last_name': 'MARINCIN'}
                 },
            'Away':
                {'HAYDN FLEURY': {'id': 8477938, 'number': '4', 'last_name': 'FLEURY'},
                 'NOAH HANIFIN': {'id': 8478396, 'number': '5', 'last_name': 'HANIFIN'},
                 'DEREK RYAN': {'id': 8478585, 'number': '7', 'last_name': 'RYAN'},
                 'JORDAN STAAL': {'id': 8473533, 'number': '11', 'last_name': 'STAAL'},
                 'JUSTIN WILLIAMS': {'id': 8468508, 'number': '14', 'last_name': 'WILLIAMS'},
                 'MARCUS KRUGER': {'id': 8475323, 'number': '16', 'last_name': 'KRUGER'},
                 'JOSH JOORIS': {'id': 8477591, 'number': '19', 'last_name': 'JOORIS'},
                 'SEBASTIAN AHO': {'id': 8478427, 'number': '20', 'last_name': 'AHO'},
                 'BRETT PESCE': {'id': 8477488, 'number': '22', 'last_name': 'PESCE'},
                 'BROCK MCGINN': {'id': 8476934, 'number': '23', 'last_name': 'MCGINN'},
                 'JUSTIN FAULK': {'id': 8475753, 'number': '27', 'last_name': 'FAULK'},
                 'ELIAS LINDHOLM': {'id': 8477496, 'number': '28', 'last_name': 'LINDHOLM'},
                 'JOAKIM NORDSTROM': {'id': 8475807, 'number': '42', 'last_name': 'NORDSTROM'},
                 'VICTOR RASK': {'id': 8476437, 'number': '49', 'last_name': 'RASK'},
                 'JEFF SKINNER': {'id': 8475784, 'number': '53', 'last_name': 'SKINNER'},
                 'TREVOR VAN RIEMSDYK': {'id': 8477845, 'number': '57', 'last_name': 'VAN RIEMSDYK'},
                 'JACCOB SLAVIN': {'id': 8476958, 'number': '74', 'last_name': 'SLAVIN'},
                 'TEUVO TERAVAINEN': {'id': 8476882, 'number': '86', 'last_name': 'TERAVAINEN'},
                 'SCOTT DARLING': {'id': 8474152, 'number': '33', 'last_name': 'DARLING'},
                 'KLAS DAHLBECK': {'id': 8476403, 'number': '6', 'last_name': 'DAHLBECK'},
                 'PHILLIP DI GIUSEPPE': {'id': 8476858, 'number': '34', 'last_name': 'DI GIUSEPPE'}
                 }
            }


@pytest.fixture
def teams():
    return {'Home': 'TOR', 'Away': 'CAR'}


@pytest.fixture
def current_score():
    return {'Home': 4, 'Away': 1}


def test_parse_event(event, players, teams, current_score):
    """ Checks that it parses an event correctly """
    parsed_event = {
        'Description': 'TOR #25 VAN RIEMSDYK\xa0Slashing(2 min), Off. Zone Drawn By: CAR #49 RASK',
        'Event': 'PENL', 'Period': 1, 'Time_Elapsed': '15:59', 'Seconds_Elapsed': 959.0, 'Ev_Team': 'TOR',
        'Home_Score': 4, 'Away_Score': 1, 'score_diff': 3, 'homePlayer1': 'MITCHELL MARNER', 'homePlayer1_id': 8478483,
        'homePlayer2': 'TYLER BOZAK', 'homePlayer2_id': 8475098, 'homePlayer3': 'JAMES VAN RIEMSDYK',
        'homePlayer3_id': 8474037, 'homePlayer4': 'ROMAN POLAK', 'homePlayer4_id': 8471392,
        'homePlayer5': 'JAKE GARDINER', 'homePlayer5_id': 8474581, 'homePlayer6': 'FREDERIK ANDERSEN',
        'homePlayer6_id': 8475883, 'awayPlayer1': 'VICTOR RASK', 'awayPlayer1_id': 8476437,
        'awayPlayer2': 'JEFF SKINNER', 'awayPlayer2_id': 8475784, 'awayPlayer3': 'TEUVO TERAVAINEN',
        'awayPlayer3_id': 8476882, 'awayPlayer4': 'NOAH HANIFIN', 'awayPlayer4_id': 8478396,
        'awayPlayer5': 'BRETT PESCE', 'awayPlayer5_id': 8477488, 'awayPlayer6': 'SCOTT DARLING',
        'awayPlayer6_id': 8474152, 'Away_Goalie': 'SCOTT DARLING', 'Away_Goalie_Id': 8474152,
        'Home_Goalie': 'FREDERIK ANDERSEN', 'Home_Goalie_Id': 8475883, 'Away_Players': 6, 'Home_Players': 6,
        'Strength': '5x5', 'Type': 'Slashing(2 min)', 'Ev_Zone': 'Off', 'Home_Zone': 'Off',
        'p1_name': 'JAMES VAN RIEMSDYK', 'p1_ID': 8474037, 'p2_name': 'VICTOR RASK', 'p2_ID': 8476437
    }

    assert parsed_event == html_pbp.parse_event(event, players, teams['Home'], current_score)


def test_parse_html(pbp_cols, players, teams, cleaned_html):
    """ Check that it parsed the entirety of the html correctly"""
    game_df = html_pbp.parse_html(cleaned_html, players, teams)

    assert isinstance(game_df, pd.DataFrame)
    assert game_df.shape[0] == 331
    assert list(game_df.columns) == pbp_cols


def test_get_pbp():
    """ Test getting the html pbp"""
    pass


def test_get_soup():
    """ Test 'soupifying' the html doc """
    pass


def test_strip_html_pbp():
    """ String the html tags and such and make a list of lists for all plays"""
    pass


def test_clean_html_pbp():
    """ Get rid of html and format the data """
    pass
