"""
Functions to scrape by season, games, and date range
"""

import time
import pandas as pd
from datetime import datetime
import hockey_scraper.nhl.game_scraper as game_scraper
import hockey_scraper.nhl.json_schedule as json_schedule
import hockey_scraper.utils.shared as shared


def print_errors(detailed=True):
    """
    Print errors with scraping.

    Detailed parameter controls if certain errors should be *re-printed* after scraping all games.
    For example if the pbp for a game is broken it's always printed immediately after that game.
    But a summary of broken games will be printed if over 25 games are scraped. The logic is that
    it'll be easier when you've scraped a lot of games to see all the errors at the end than scrolling
    though all the output and potentially missing it.

    :param detailed: When False only print player IDs otherwise all
    
    :return: None
    """
    print("")

    if game_scraper.broken_pbp_games and detailed:
        print('Broken pbp:')
        for x in game_scraper.broken_pbp_games:
            print("  -", x[0], x[1])
        print("")

    if game_scraper.broken_shifts_games and detailed:
        print('Broken shifts:')
        for x in game_scraper.broken_shifts_games:
            print("  -", x[0], x[1])
        print("")

    if game_scraper.missing_coords and detailed:
        print('Games missing coordinates:')
        for x in game_scraper.missing_coords:
            print("  -", x[0], x[1])
        print("")

    if game_scraper.players_missing_ids:
        print("Players missing IDs:")
        for x in game_scraper.players_missing_ids:
            print("  -", x[0], x[1])
        print("")

    # Clear them all out for the next call
    game_scraper.broken_shifts_games = []
    game_scraper.broken_pbp_games = []
    game_scraper.players_missing_ids = []
    game_scraper.missing_coords = []


def scrape_list_of_games(games, if_scrape_shifts, verbose=False):
    """
    Given a list of game_id's (and a date for each game) it scrapes them
    
    :param games: list of [game_id, date]
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts
    :params verbose: Verbosity when printing errors. Defaults to False    
    
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
        shifts_df = pd.concat(shifts_dfs).reset_index(drop=True)
    else:
        shifts_df = None

    # Only print full details when # games > 25 or verbose=True
    error_verbosity = verbose or len(games) >= 25
    print_errors(error_verbosity)

    return pbp_df, shifts_df


def scrape_schedule(from_date, to_date, data_format='pandas', rescrape=False, docs_dir=False):
    """
    Scrape the games schedule in a given range.
    
    :param from_date: date you want to scrape from
    :param to_date: date you want to scrape to 
    :param data_format: format you want data in - csv or  pandas (pandas is default)
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir. (def. = None)
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping. When True it'll refer to (or if needed create) such a repository in the home
                     directory. When provided a string it'll try to use that. Here it must be a valid directory otheriwse
                     it won't work (I won't make it for you). When False the files won't be saved.
    
    :return: DataFrame of None
    """
    cols = ["game_id", "date", "venue", "home_team", "away_team", "start_time", "home_score", "away_score", "status"]

    shared.check_data_format(data_format)
    shared.check_valid_dates(from_date, to_date)

    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    print("Scraping the schedule between {} and {}".format(from_date, to_date))

    # live = True allows us to scrape games that aren't final
    sched = json_schedule.scrape_schedule(from_date, to_date, preseason=True, not_over=True)
    sched_df = pd.DataFrame(sched, columns=cols)

    if data_format.lower() == 'csv':
        shared.to_csv(from_date + '--' + to_date, sched_df, "nhl", "schedule")
    else:
        return sched_df


def scrape_date_range(from_date, to_date, if_scrape_shifts, data_format='csv', preseason=False, rescrape=False, docs_dir=False, verbose=False):
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
                     in after scraping. When True it'll refer to (or if needed create) such a repository in the home
                     directory. When provided a string it'll try to use that. Here it must be a valid directory otheriwse
                     it won't work (I won't make it for you). When False the files won't be saved.
    :params verbose: Override default verbosity when printing errors

    :return: Dictionary with DataFrames and errors or None
    """
    shared.check_data_format(data_format)
    shared.check_valid_dates(from_date, to_date)

    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    games = json_schedule.scrape_schedule(from_date, to_date, preseason)
    pbp_df, shifts_df = scrape_list_of_games(games, if_scrape_shifts, verbose)

    if data_format.lower() == 'csv':
        shared.to_csv(from_date + '--' + to_date, pbp_df, "nhl", "pbp")
        shared.to_csv(from_date + '--' + to_date, shifts_df, "nhl", "shifts")
    else:
        return {"pbp": pbp_df, "shifts": shifts_df} if if_scrape_shifts else {"pbp": pbp_df}


def scrape_seasons(seasons, if_scrape_shifts, data_format='csv', preseason=False, rescrape=False, docs_dir=False, verbose=False):
    """
    Given list of seasons it scrapes all the seasons 
    
    :param seasons: list of seasons
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param preseason: Boolean indicating whether to include preseason games (default if False)
                      This is may or may not work!!! I don't give a shit.
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir.
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping. When True it'll refer to (or if needed create) such a repository in the home
                     directory. When provided a string it'll try to use that. Here it must be a valid directory otheriwse
                     it won't work (I won't make it for you). When False the files won't be saved.
    :params verbose: Override default verbosity when printing errors

    :return: Dictionary with DataFrames and errors or None
    """
    shared.check_data_format(data_format)
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    # Holds all seasons scraped (if not csv)
    master_pbps, master_shifts = [], []

    for season in seasons:
        from_date = shared.season_start_bound(season)
        to_date = datetime.strftime(shared.season_end_bound(str(int(season) + 1)), "%Y-%m-%d")

        games = json_schedule.scrape_schedule(from_date, to_date, preseason)
        pbp_df, shifts_df = scrape_list_of_games(games, if_scrape_shifts, verbose)

        if data_format.lower() == 'csv':
            shared.to_csv(str(season) + str(season + 1), pbp_df, "nhl", "pbp")
            shared.to_csv(str(season) + str(season + 1), shifts_df, "nhl", "shifts")
        elif pbp_df is not None:
            master_pbps.append(pbp_df)
            master_shifts.append(shifts_df)

    if data_format.lower() == 'pandas' and master_pbps:
        if if_scrape_shifts:
            return {"pbp": pd.concat(master_pbps), "shifts": pd.concat(master_shifts)}
        else:
            return {"pbp": pd.concat(master_pbps)}


def scrape_games(games, if_scrape_shifts, data_format='csv', rescrape=False, docs_dir=False, verbose=False):
    """
    Scrape a list of games
    
    :param games: list of game_ids
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    :param data_format: format you want data in - csv or pandas (csv is default)
    :param rescrape: If you want to rescrape pages already scraped. Only applies if you supply a docs dir.
    :param docs_dir: Directory that either contains previously scraped docs or one that you want them to be deposited 
                     in after scraping. When True it'll refer to (or if needed create) such a repository in the home
                     directory. When provided a string it'll try to use that. Here it must be a valid directory otheriwse
                     it won't work (I won't make it for you). When False the files won't be saved. 
    :params verbose: Override default verbosity when printing errors

    :return: Dictionary with DataFrames and errors or None
    """
    shared.check_data_format(data_format)
    shared.add_dir(docs_dir)
    shared.if_rescrape(rescrape)

    # Create List of game_id's and dates
    games_list = json_schedule.get_dates(games)

    # Scrape pbp and shifts
    pbp_df, shifts_df = scrape_list_of_games(games_list, if_scrape_shifts, verbose)

    if data_format.lower() == 'csv':
        shared.to_csv(str(int(time.time())), pbp_df, "nhl", "pbp")
        shared.to_csv(str(int(time.time())), shifts_df, "nhl", "shifts")
    else:
        return {"pbp": pbp_df, "shifts": shifts_df} if if_scrape_shifts else {"pbp": pbp_df}
