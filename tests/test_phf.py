""" Tests for Scraping PHF games """

import pandas as pd
import pytest

from hockey_scraper.phf import game_pbp
from hockey_scraper.phf import scrape_functions, scrape_schedule

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

def test_scrape_something_anything(pbp_columns, shifts_columns):
    """
    Just try to scrape something, please.
    """

    # 1. Just try it.
    pbp = game_pbp.scrape_pbp("612249")
    assert isinstance(pbp, pd.DataFrame)
