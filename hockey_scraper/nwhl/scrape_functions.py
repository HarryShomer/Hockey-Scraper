"""
Functions to scrape by season, games, and date range
"""
import random
import pandas as pd

#from . import html_schedule, json_pbp
import hockey_scraper.utils.shared as shared

# All columns for the pbp
cols = ['game_id', 'date', 'season', 'period', 'seconds_elapsed', 'event', 'ev_team', 'home_team', 'away_team',
        'p1_name', 'p1_id', 'p2_name', 'p2_id', 'p3_name', 'p3_id',
        "homePlayer1", "homePlayer1_id", "homePlayer2", "homePlayer2_id", "homePlayer3", "homePlayer3_id",
        "homePlayer4", "homePlayer4_id", "homePlayer5", "homePlayer5_id", "homePlayer6", "homePlayer6_id",
        "awayPlayer1", "awayPlayer1_id", "awayPlayer2", "awayPlayer2_id", "awayPlayer3", "awayPlayer3_id",
        "awayPlayer4", "awayPlayer4_id", "awayPlayer5", "awayPlayer5_id", "awayPlayer6", "awayPlayer6_id",
        'home_goalie', 'home_goalie_id', 'away_goalie', 'away_goalie_id', 'details', 'home_score', 'away_score',
        'xC', 'yC']

# Hold any games we didn't scrape for any reason
broken_games = []


def print_errors():
    """
    Print any scraping errors.
    
    :return: None
    """
    global broken_games
    if broken_games:
        print('\nBroken pbp:')
        for x in broken_games:
            print(x)

    broken_games = []


def scrape_list_of_games(games):
    """
    Scrape an arbitrary list of games given the game id's
    
    :param games: List of game_id's to scrape
    
    :return: DataFrame of pbp info 
    """
    pbp_dfs = []
    for game in games:
        print(' '.join(['Scraping NWHL Game ', str(game)]))
        pbp_df = json_pbp.scrape_pbp(game)
        if not pbp_df.empty:
            pbp_dfs.append(pbp_df)
        else:
            broken_games.append(game)

    # If not empty...
    if pbp_dfs:
        return pd.concat(pbp_dfs, sort=True).reset_index(drop=True)[cols]
    return None


def scrape_games(games, data_format='csv', rescrape=False, docs_dir=None):
    """
    Scrape a list of games

    :param games: list of game_ids
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir.
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping

    :return: Dictionary with DataFrames or None
    """
    # First check if the inputs are good
    shared.check_data_format(data_format)

    # Check on the docs_dir and re_scrape
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    pbp_df = scrape_list_of_games(games)
    print_errors()

    if data_format.lower() == 'csv':
        shared.to_csv(str(random.randint(1, 101)), pbp_df, None, "nwhl")
    else:
        return pbp_df


def scrape_date_range(from_date, to_date, data_format='csv', rescrape=False, docs_dir=None):
    """
    Scrape games in given date range

    :param from_date: date you want to scrape from
    :param to_date: date you want to scrape to
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir. (def. = None)
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping. (default is None)

    :return: Dictionary with DataFrames and errors or None
    """
    # First check if the inputs are good
    shared.check_data_format(data_format)
    shared.check_valid_dates(from_date, to_date)

    # Check on the docs_dir and re_scrape
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    # Get dates and convert to just a list of game ids
    games = html_schedule.scrape_dates(from_date, to_date)
    game_ids = [game['game_id'] for game in games]

    # Scrape all PBP
    pbp_df = scrape_list_of_games(game_ids)

    # Merge in subtype
    pbp_df = pd.merge(pbp_df, pd.DataFrame(games, columns=['game_id', 'sub_type']), on="game_id", how="left")

    print_errors()
    if data_format.lower() == 'csv':
        shared.to_csv(from_date + '--' + to_date, pbp_df, None, "nwhl")
    else:
        return pbp_df


def scrape_seasons(seasons, data_format='csv', rescrape=False, docs_dir=None):
    """
    Given list of seasons it scrapes all the seasons 

    :param seasons: list of seasons
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir.
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping

    :return: Dictionary with DataFrames and errors or None
    """
    # First check if the inputs are good
    shared.check_data_format(data_format)

    # Check on the docs_dir and re_scrape
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    # Holds all seasons scraped (if not csv)
    master_pbps = []

    for season in seasons:
        games = html_schedule.scrape_seasons(season)
        game_ids = [game['game_id'] for game in games]

        # Scrape all PBP
        pbp_df = scrape_list_of_games(game_ids)

        # Merge in subtype
        pbp_df = pd.merge(pbp_df, pd.DataFrame(games, columns=['game_id', 'sub_type']), on="game_id", how="left")

        if data_format.lower() == 'csv':
            shared.to_csv(str(season) + str(season + 1), pbp_df, None, "nwhl")
        else:
            master_pbps.append(pbp_df)

    print_errors()
    if data_format.lower() == 'pandas':
        return pd.concat(master_pbps, sort=True)

