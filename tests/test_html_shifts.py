""" Tests for 'html_shifts.py' """

import bs4
import pandas as pd
import pytest

from hockey_scraper.nhl.shifts import html_shifts


@pytest.fixture
def shift_cols():
    return ['Game_Id', 'Period', 'Team', 'Player', 'Player_Id', 'Start', 'End', 'Duration']


@pytest.fixture
def game_id():
    return '2009020001'

@pytest.fixture
def player_ids():
    return {
        'Home': {
                  'DENNIS WIDEMAN': {'id': 8469770, 'number': '6', 'last_name': 'WIDEMAN'},
                  'CHUCK KOBASEW': {'id': 8469467, 'number': '12', 'last_name': 'KOBASEW'},
                  'MARCO STURM': {'id': 8464979, 'number': '16', 'last_name': 'STURM'},
                  'MILAN LUCIC': {'id': 8473473, 'number': '17', 'last_name': 'LUCIC'},
                  'ANDREW FERENCE': {'id': 8466333, 'number': '21', 'last_name': 'FERENCE'},
                  'SHAWN THORNTON': {'id': 8465978, 'number': '22', 'last_name': 'THORNTON'},
                  'BLAKE WHEELER': {'id': 8471218, 'number': '26', 'last_name': 'WHEELER'},
                  'STEVE BEGIN': {'id': 8464994, 'number': '27', 'last_name': 'BEGIN'},
                  'MARK RECCHI': {'id': 8450725, 'number': '28', 'last_name': 'RECCHI'},
                  'ZDENO CHARA': {'id': 8465009, 'number': '33', 'last_name': 'CHARA'},
                  'PATRICE BERGERON': {'id': 8470638, 'number': '37', 'last_name': 'BERGERON'},
                  'MARK STUART': {'id': 8470614, 'number': '45', 'last_name': 'STUART'},
                  'DAVID KREJCI': {'id': 8471276, 'number': '46', 'last_name': 'KREJCI'},
                  'MATT HUNWICK': {'id': 8471436, 'number': '48', 'last_name': 'HUNWICK'},
                  'DEREK MORRIS': {'id': 8464966, 'number': '53', 'last_name': 'MORRIS'},
                  'BYRON BITZ': {'id': 8470700, 'number': '61', 'last_name': 'BITZ'},
                  'MICHAEL RYDER': {'id': 8467545, 'number': '73', 'last_name': 'RYDER'},
                  'MARC SAVARD': {'id': 8462118, 'number': '91', 'last_name': 'SAVARD'},
                  'TIM THOMAS': {'id': 8460703, 'number': '30', 'last_name': 'THOMAS'},
                  'JOHNNY BOYCHUK': {'id': 8470187, 'number': '55', 'last_name': 'BOYCHUK'}
                  },
        'Away': {
                  'BRIAN POTHIER': {'id': 8468427, 'number': '2', 'last_name': 'POTHIER'},
                  'TOM POTI': {'id': 8465012, 'number': '3', 'last_name': 'POTI'},
                  'JOHN ERSKINE': {'id': 8467365, 'number': '4', 'last_name': 'ERSKINE'},
                  'ALEX OVECHKIN': {'id': 8471214, 'number': '8', 'last_name': 'OVECHKIN'},
                  'BRENDAN MORRISON': {'id': 8459461, 'number': '9', 'last_name': 'MORRISON'},
                  'MATT BRADLEY': {'id': 8465059, 'number': '10', 'last_name': 'BRADLEY'},
                  'BOYD GORDON': {'id': 8470159, 'number': '15', 'last_name': 'GORDON'},
                  'CHRIS CLARK': {'id': 8460567, 'number': '17', 'last_name': 'CLARK'},
                  'NICKLAS BACKSTROM': {'id': 8473563, 'number': '19', 'last_name': 'BACKSTROM'},
                  'BROOKS LAICH': {'id': 8469639, 'number': '21', 'last_name': 'LAICH'},
                  'MIKE KNUBLE': {'id': 8458590, 'number': '22', 'last_name': 'KNUBLE'},
                  'MILAN JURCINA': {'id': 8469684, 'number': '23', 'last_name': 'JURCINA'},
                  'SHAONE MORRISONN': {'id': 8469472, 'number': '26', 'last_name': 'MORRISONN'},
                  'ALEXANDER SEMIN': {'id': 8470120, 'number': '28', 'last_name': 'SEMIN'},
                  'BOYD KANE': {'id': 8465028, 'number': '34', 'last_name': 'KANE'},
                  'DAVID STECKEL': {'id': 8469483, 'number': '39', 'last_name': 'STECKEL'},
                  'MIKE GREEN': {'id': 8471242, 'number': '52', 'last_name': 'GREEN'},
                  'QUINTIN LAING': {'id': 8466232, 'number': '53', 'last_name': 'LAING'},
                  'JOSE THEODORE': {'id': 8460535, 'number': '60', 'last_name': 'THEODORE'},
                  'JEFF SCHULTZ': {'id': 8471240, 'number': '55', 'last_name': 'SCHULTZ'},
                  'TYLER SLOAN': {'id': 8468846, 'number': '89', 'last_name': 'SLOAN'},
                  'MICHAEL NYLANDER': {'id': 8458573, 'number': '92', 'last_name': 'NYLANDER'}
        }
    }


@pytest.fixture
def shifts_html():
    home, away = html_shifts.get_shifts("2009020001")
    return {'home': home, 'away': away}


@pytest.fixture
def shifts_dfs(shifts_html, player_ids, game_id):
    home_df = html_shifts.parse_html(shifts_html['home'], player_ids, game_id)
    away_df = html_shifts.parse_html(shifts_html['away'], player_ids, game_id)

    return {'home': home_df, 'away': away_df}


def test_get_shifts(shifts_html):
    """ Test getting both shifts pages """
    assert type(shifts_html['home']) == str
    assert len(shifts_html['home']) > 0

    assert type(shifts_html['away']) == str
    assert len(shifts_html['away']) > 0


def test_get_soup(shifts_html):
    """ Test get soup -> Returns td tags for pbp and= list of both teams"""

    # Home
    td, teams = html_shifts.get_soup(shifts_html['home'])
    assert type(td) == bs4.element.ResultSet
    assert len(td) > 100   # If it's greater than 100 it's fine
    assert type(teams) == list
    assert len(teams) == 2

    # Away
    td, teams = html_shifts.get_soup(shifts_html['away'])
    assert type(td) == bs4.element.ResultSet
    assert len(td) > 100  # If it's greater than 100 it's fine
    assert type(teams) == list
    assert len(teams) == 2


def test_analyze_shifts(player_ids):
    """ Test analyzing a single shift. See if it parses it correctly"""
    # Get html (one td) and see if it spits out the correct info
    shift = ['30', '3', '17:05 / 2:55', '18:03 / 1:57', '00:58']
    name = "DENNIS WIDEMAN"
    team = "BOSTON BRUINS"
    home_team = "BOSTON BRUINS"
    parsed_shift = {'Player': 'DENNIS WIDEMAN', 'Period': '3', 'Team': 'BOS', 'Start': 1025.0, 'Duration': 58.0,
                    'End': 1083.0, 'Player_Id': 8469770}

    assert parsed_shift == html_shifts.analyze_shifts(shift, name, team, home_team, player_ids)


def test_parse_html(shifts_dfs, shift_cols):
    """ Should return a DataFrame of all the shifts for a given team 
        Here we make sure it works for both the home and away teams
    """
    # Check they are both DataFrames
    assert isinstance(shifts_dfs['home'], pd.DataFrame)
    assert isinstance(shifts_dfs['away'], pd.DataFrame)

    # Check correct amount of rows for each
    assert shifts_dfs['home'].shape[0] == 360
    assert shifts_dfs['away'].shape[0] == 375

    # Correct columns for each
    assert list(shifts_dfs['home'].columns).sort() == shift_cols.sort()
    assert list(shifts_dfs['away'].columns).sort() == shift_cols.sort()


def test_scrape_game(game_id, player_ids, shifts_dfs, shift_cols):
    """ Should return DataFrame with both home and away shifts """
    # Return Df
    # Correct amount of line  -- Confirm equals to home + away
    # Correct columns
    game_df = html_shifts.scrape_game(game_id, player_ids)

    # Check if it's the right datatype
    assert isinstance(game_df, pd.DataFrame)

    # Same number of rows as correct value and addition of home and aways dfs
    assert game_df.shape[0] == (shifts_dfs['home'].shape[0] + shifts_dfs['away'].shape[0]) == 735

    # Correct columns
    assert list(shifts_dfs['home'].columns).sort() == shift_cols.sort()
