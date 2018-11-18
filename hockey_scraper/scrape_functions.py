"""
Functions to scrape by season, games, and date range
"""

import hockey_scraper.json_schedule as json_schedule
import hockey_scraper.game_scraper as game_scraper
import hockey_scraper.shared as shared
import pandas as pd
import time
import random


# This hold the scraping errors in a string format.
# This may seem pointless but I have a personal reason for it (I think...)
errors = ''


def print_errors():
    """
    Print errors with scraping.
    
    Also puts errors in the "error" string (would just print the string but it would look like shit on one line. I
    could store it as I "should" print it but that isn't how I want it). 

    :return: None
    """
    global errors

    if game_scraper.broken_pbp_games:
        print('\nBroken pbp:')
        errors += 'Broken pbp:'
        for x in game_scraper.broken_pbp_games:
            print(x[0], x[1])
            errors = ' '.join([errors, str(x[0]), ","])

    if game_scraper.broken_shifts_games:
        print('\nBroken shifts:')
        errors += 'Broken shifts:'
        for x in game_scraper.broken_shifts_games:
            print(x[0], x[1])
            errors = ' '.join([errors, str(x[0]), ","])

    if game_scraper.players_missing_ids:
        print("\nPlayers missing ID's:")
        errors += "Players missing ID's:"
        for x in game_scraper.players_missing_ids:
            print(x[0], x[1])
            errors = ' '.join([errors, str(x[0]), ","])

    if game_scraper.missing_coords:
        print('\nGames missing coordinates:')
        errors += 'Games missing coordinates:'
        for x in game_scraper.missing_coords:
            print(x[0], x[1])
            errors = ' '.join([errors, str(x[0]), ","])

    print('\n')

    # Clear them all out for the next call
    game_scraper.broken_shifts_games = []
    game_scraper.broken_pbp_games = []
    game_scraper.players_missing_ids = []
    game_scraper.missing_coords = []


def check_data_format(data_format):
    """
    Checks if data_format specified (if it is at all) is either None, 'Csv', or 'pandas'.
    It exits program with error message if input isn't good.
    
    :param data_format: data_format provided 
    
    :return: Boolean - True if good
    """
    if not data_format or data_format.lower() not in ['csv', 'pandas']:
        raise shared.HaltException('{} is an unspecified data format. The two options are Csv and Pandas '
                                   '(Csv is default)\n'.format(data_format))


def check_valid_dates(from_date, to_date):
    """
    Check if it's a valid date range
    
    :param from_date: date should scrape from
    :param to_date: date should scrape to
    
    :return: None
    """
    try:
        if time.strptime(to_date, "%Y-%m-%d") < time.strptime(from_date, "%Y-%m-%d"):
            raise shared.HaltException("Error: The second date input is earlier than the first one")
    except ValueError:
        raise shared.HaltException("Error: Incorrect format given for dates. They must be given like 'yyyy-mm-dd' "
                                   "(ex: '2016-10-01').")


def to_csv(file_name, pbp_df, shifts_df):
    """
    Write DataFrame(s) to csv file(s)
    
    :param file_name: name of file
    :param pbp_df: pbp DataFrame
    :param shifts_df: shifts DataFrame
    
    :return: None
    """
    if pbp_df is not None:
        print("\nPbp data deposited in file - " + 'nhl_pbp{}.csv'.format(file_name))
        pbp_df.to_csv('nhl_pbp{}.csv'.format(file_name), sep=',', encoding='utf-8')
    if shifts_df is not None:
        print("Shift data deposited in file - " + 'nhl_shifts{}.csv'.format(file_name))
        shifts_df.to_csv('nhl_shifts{}.csv'.format(file_name), sep=',', encoding='utf-8')


def scrape_list_of_games(games, if_scrape_shifts):
    """
    Given a list of game_id's (and a date for each game) it scrapes them
    
    :param games: list of [game_id, date]
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts     
    
    :return: DataFrame of pbp info, also shifts if specified
    """
    pbp_dfs = []
    shifts_dfs = []

    for game in games:
        pbp_df, shifts_df = game_scraper.scrape_game(str(game["game_id"]), game["date"], if_scrape_shifts)
        if pbp_df is not None:
            pbp_dfs.extend([pbp_df])
        if shifts_df is not None:
            shifts_dfs.extend([shifts_df])

    # Check if any games...if not let's get out of here
    if len(pbp_dfs) == 0:
        return None, None
    else:
        pbp_df = pd.concat(pbp_dfs)
        pbp_df = pbp_df.reset_index(drop=True)
        pbp_df.apply(lambda row: game_scraper.check_goalie(row), axis=1)

    if if_scrape_shifts:
        shifts_df = pd.concat(shifts_dfs)
        shifts_df = shifts_df.reset_index(drop=True)
    else:
        shifts_df = None

    # Print all errors associated with scrape call
    print_errors()

    return pbp_df, shifts_df


def scrape_date_range(from_date, to_date, if_scrape_shifts, data_format='csv', preseason=False, rescrape=False, docs_dir=None):
    """
    Scrape games in given date range
    
    :param from_date: date you want to scrape from
    :param to_date: date you want to scrape to
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or  pandas (csv is default)
    :param preseason: Boolean indicating whether to include preseason games (default if False)
                      This is may or may not work!!! I don't give a shit.
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir. (def. = None)
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping. (default is None)
    
    :return: Dictionary with DataFrames and errors or None
    """
    # First check if the inputs are good
    check_data_format(data_format)
    check_valid_dates(from_date, to_date)

    # Check on the docs_dir and re_scrape
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    games = json_schedule.scrape_schedule(from_date, to_date, preseason)
    pbp_df, shifts_df = scrape_list_of_games(games, if_scrape_shifts)

    if data_format.lower() == 'csv':
        to_csv(from_date+'--'+to_date, pbp_df, shifts_df)
    else:
        return {"pbp": pbp_df, "shifts": shifts_df, "errors": errors} if if_scrape_shifts else {"pbp": pbp_df,
                                                                                                "errors": errors}


def scrape_seasons(seasons, if_scrape_shifts, data_format='csv', preseason=False, rescrape=False, docs_dir=None):
    """
    Given list of seasons it scrapes all the seasons 
    
    :param seasons: list of seasons
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param preseason: Boolean indicating whether to include preseason games (default if False)
                      This is may or may not work!!! I don't give a shit.
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir.
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping
    
    :return: Dictionary with DataFrames and errors or None
    """
    # First check if the inputs are good
    check_data_format(data_format)

    # Check on the docs_dir and re_scrape
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    # Holds all seasons scraped (if not csv)
    master_pbps, master_shifts = [], []

    for season in seasons:
        from_date = '-'.join([str(season), '9', '1'])
        to_date = '-'.join([str(season + 1), '7', '1'])

        games = json_schedule.scrape_schedule(from_date, to_date, preseason)
        pbp_df, shifts_df = scrape_list_of_games(games, if_scrape_shifts)

        if data_format.lower() == 'csv':
            to_csv(str(season)+str(season+1), pbp_df, shifts_df)
        else:
            master_pbps.append(pbp_df)
            master_shifts.append(shifts_df)

    if data_format.lower() == 'pandas':
        if if_scrape_shifts:
            return {"pbp": pd.concat(master_pbps), "shifts": pd.concat(master_shifts), "errors": errors}
        else:
            return {"pbp": pd.concat(master_pbps), "errors": errors}


def scrape_games(games, if_scrape_shifts, data_format='csv', rescrape=False, docs_dir=None):
    """
    Scrape a list of games
    
    :param games: list of game_ids
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir.
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping
    
    :return: Dictionary with DataFrames and errors or None
    """
    # First check if the inputs are good
    check_data_format(data_format)

    # Check on the docs_dir and re_scrape
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    # Create List of game_id's and dates
    games_list = json_schedule.get_dates(games)

    # Scrape pbp and shifts
    pbp_df, shifts_df = scrape_list_of_games(games_list, if_scrape_shifts)

    if data_format.lower() == 'csv':
        to_csv(str(random.randint(1, 101)), pbp_df, shifts_df)
    else:
        return {"pbp": pbp_df, "shifts": shifts_df, "errors": errors} if if_scrape_shifts else {"pbp": pbp_df,
                                                                                                "errors": errors}
