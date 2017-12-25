"""
Functions to scrape by season, games, and date range
"""

import hockey_scraper.json_schedule as json_schedule
import hockey_scraper.game_scraper as game_scraper
import pandas as pd
import time
import random
import json


def check_data_format(data_format):
    """
    Checks if data_format specified (if it is at all) is either None, 'Csv', or 'json'.
    It exits program with error message if input isn't good.
    
    :param data_format: data_format provided 
    
    :return: None
    """
    if not data_format or data_format.lower() not in ['csv', 'json']:
        print('{} is an unspecified data format. The two options are Csv and Json (Csv is default)\n'.format(data_format))
        exit()


def check_valid_dates(from_date, to_date):
    """
    Check if it's a valid date range
    
    :param from_date: date should scrape from
    :param to_date: date should scrape to
    
    :return: None, will exit if not valid
    """
    try:
        if time.strptime(to_date, "%Y-%m-%d") < time.strptime(from_date, "%Y-%m-%d"):
            print("Error: The second date input is earlier than the first one")
            exit()
    except ValueError:
        print("Error: Incorrect format given for dates. They must be given like 'yyyy-mm-dd' (ex: '2016-10-01').")
        exit()


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
        pbp_df.to_csv('nhl_pbp{}.csv'.format(file_name), sep=',')
    if shifts_df is not None:
        print("Shift data deposited in file - " + 'nhl_shifts{}.csv'.format(file_name))
        shifts_df.to_csv('nhl_shifts{}.csv'.format(file_name), sep=',')


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
        pbp_df, shifts_df = game_scraper.scrape_game(str(game[0]), game[1], if_scrape_shifts)
        if pbp_df is not None:
            pbp_dfs.extend([pbp_df])
        if shifts_df is not None:
            shifts_dfs.extend([shifts_df])

    # Check if any games
    if len(pbp_dfs) == 0:
        return None, None

    pbp_df = pd.concat(pbp_dfs)
    pbp_df = pbp_df.reset_index(drop=True)
    pbp_df.apply(lambda row: game_scraper.check_goalie(row), axis=1)

    if if_scrape_shifts:
        shifts_df = pd.concat(shifts_dfs)
        shifts_df = shifts_df.reset_index(drop=True)
    else:
        shifts_df = None

    return pbp_df, shifts_df


def scrape_date_range(from_date, to_date, if_scrape_shifts, data_format='csv', preseason=False):
    """
    Scrape games in given date range
    
    :param from_date: date you want to scrape from
    :param to_date: date you want to scrape to
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or json (csv is default)
    :param preseason: Boolean indicating whether include preseason games (default if False)
    
    :return: Json string or None
    """
    check_data_format(data_format)
    check_valid_dates(from_date, to_date)

    json_dfs = dict()  # Holds json of data if choose to return that

    games = json_schedule.scrape_schedule(from_date, to_date, preseason)
    pbp_df, shifts_df = scrape_list_of_games(games, if_scrape_shifts)

    if data_format.lower() == 'csv':
        to_csv(from_date+'--'+to_date, pbp_df, shifts_df)
    else:
        if pbp_df is not None:
            json_dfs['pbp'] = pbp_df.to_dict('records')
        if shifts_df is not None:
            json_dfs['shifts'] = shifts_df.to_dict('records')

    # Print all errors associated with scrape call
    game_scraper.print_errors()

    # If we have something in there that means json was chosen
    if len(json_dfs.keys()) > 0:
        return json.dumps(json_dfs)


def scrape_seasons(seasons, if_scrape_shifts, data_format='csv', preseason=False):
    """
    Given list of seasons it scrapes all the seasons 
    
    :param seasons: list of seasons
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or json (csv is default)
    :param preseason: Boolean indicating whether include preseason games (default if False)
    
    :return: Json string or None
    """
    check_data_format(data_format)

    json_dfs = {'pbp': dict(), 'shifts': dict()}  # Holds json of data if choose to return that

    for season in seasons:
        from_date = '-'.join([str(season), '9', '1'])
        to_date = '-'.join([str(season + 1), '7', '1'])

        games = json_schedule.scrape_schedule(from_date, to_date, preseason)
        pbp_df, shifts_df = scrape_list_of_games(games, if_scrape_shifts)

        if data_format.lower() == 'csv':
            to_csv(str(season)+str(season+1), pbp_df, shifts_df)
        else:
            if pbp_df is not None:
                json_dfs['pbp'][str(season)] = pbp_df.to_dict('records')
            if shifts_df is not None:
                json_dfs['shifts'][str(season)] = shifts_df.to_dict('records')

    # Print all errors associated with scrape call
    game_scraper.print_errors()

    # If we have something in there that means json was chosen
    if len(json_dfs['pbp'].keys()) > 0:
        return json.dumps(json_dfs)


def scrape_games(games, if_scrape_shifts, data_format='csv'):
    """
    Scrape a list of games
    
    :param games: list of game_ids
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or json (csv is default)
    :param preseason: Boolean indicating whether include preseason games (default if False)
    
    :return: Json string or None
    """
    check_data_format(data_format)

    json_dfs = dict()   # Holds json of data if choose to return that

    # Create List of game_id's and dates
    games_list = json_schedule.get_dates(games)

    # Scrape pbp and shifts
    pbp_df, shifts_df = scrape_list_of_games(games_list, if_scrape_shifts)

    if data_format.lower() == 'csv':
        to_csv(str(random.randint(1, 101)), pbp_df, shifts_df)
    else:
        if pbp_df is not None:
            json_dfs['pbp'] = pbp_df.to_dict('records')
        if shifts_df is not None:
            json_dfs['shifts'] = shifts_df.to_dict('records')

    # Print all errors associated with scrape call
    game_scraper.print_errors()

    if len(json_dfs.keys()) > 0:
        return json.dumps(json_dfs)










