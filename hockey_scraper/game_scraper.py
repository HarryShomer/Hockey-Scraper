"""
This module contains code to scrape data for a single game
"""

import hockey_scraper.json_pbp as json_pbp
import hockey_scraper.html_pbp as html_pbp
import hockey_scraper.espn_pbp as espn_pbp
import hockey_scraper.json_shifts as json_shifts
import hockey_scraper.html_shifts as html_shifts
import hockey_scraper.playing_roster as playing_roster
import hockey_scraper.shared as shared
import pandas as pd

broken_shifts_games = []
broken_pbp_games = []
players_missing_ids = []
espn_games = []
missing_coords = []


pbp_columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
           'Ev_Zone', 'Type', 'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
           'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
           'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
           'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
           'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
           'homePlayer6_id',  'Away_Players', 'Home_Players', 'Away_Score', 'Home_Score', 'Away_Goalie',
           'Away_Goalie_Id', 'Home_Goalie', 'Home_Goalie_Id', 'xC', 'yC', 'Home_Coach', 'Away_Coach']


def check_goalie(row):
    """
    Checks for bad goalie names (you can tell by them having no player id)
    
    :param row: df row
    
    :return: None
    """
    if row['Away_Goalie'] != '' and row['Away_Goalie_Id'] == 'NA':
        if [row['Away_Goalie'], row['Game_Id']] not in players_missing_ids:
            players_missing_ids.extend([[row['Away_Goalie'], row['Game_Id']]])

    if row['Home_Goalie'] != '' and row['Home_Goalie_Id'] == 'NA':
        if [row['Home_Goalie'], row['Game_Id']] not in players_missing_ids:
            players_missing_ids.extend([[row['Home_Goalie'], row['Game_Id']]])


def get_players_json(json):
    """
    Return dict of players for that game
    
    :param json: gameData section of json
    
    :return: dict of players->keys are the name (in uppercase)  
    """
    players = dict()

    players_json = json['players']
    for key in players_json.keys():
        name = shared.fix_name(players_json[key]['fullName'].upper())
        players[name] = {'id': ' '}
        try:
            players[name]['id'] = players_json[key]['id']
        except KeyError:
            print(name, ' is missing an ID number in the pbp json')
            players[name]['id'] = 'NA'

    return players


def combine_players_lists(json_players, roster_players, game_id):
    """
    Combine the json list of players (which contains id's) with the list in the roster html
    
    :param json_players: dict of all players with id's
    :param roster_players: dict with home and and away keys for players
    :param game_id: id of game
    
    :return: dict containing home and away keys -> which contains list of info on each player
    """
    players = {'Home': dict(), 'Away': dict()}

    for venue in players.keys():
        for player in roster_players[venue]:
            try:
                name = shared.fix_name(player[2])
                player_id = json_players[name]['id']
                players[venue][name] = {'id': player_id, 'number': player[0]}
            except KeyError:
                # If he was listed as a scratch and not a goalie (check_goalie deals with goalies)
                # As a whole the scratch list shouldn't be trusted but if a player is missing an id # and is on the
                # scratch list I'm willing to assume that he didn't play
                if not player[3] and player[1] != 'G':
                    player.extend([game_id])
                    players_missing_ids.extend([[player[2], player[4]]])
                    players[venue][name] = {'id': 'NA', 'number': player[0]}

    return players


def get_teams_and_players(game_json, roster, game_id):
    """
    Get list of players and teams for game
    
    :param game_json: json pbp for game
    :param roster: players from roster html
    :param game_id: id for game
    
    :return: dict for both - players and teams
    """
    try:
        teams = json_pbp.get_teams(game_json)
        player_ids = get_players_json(game_json['gameData'])
        players = combine_players_lists(player_ids, roster['players'], game_id)
    except Exception as e:
        print('Problem with getting the teams or players', e)
        return None, None

    return players, teams


def combine_html_json_pbp(json_df, html_df, game_id, date):
    """
    Join both data sources
    
    :param json_df: json pbp DataFrame
    :param html_df: html pbp DataFrame
    :param game_id: id of game
    :param date: date of game
    
    :return: finished pbp
    """
    try:
        html_df.Period = html_df.Period.astype(int)
        game_df = pd.merge(html_df, json_df, left_on=['Period', 'Event', 'Seconds_Elapsed'],
                           right_on=['period', 'event', 'seconds_elapsed'], how='left')

        # This id because merge doesn't work well with shootouts
        game_df = game_df.drop_duplicates(subset=['Period', 'Event', 'Description', 'Seconds_Elapsed'])
    except Exception as e:
        print('Problem combining Html Json pbp for game {}'.format(game_id, e))
        return

    game_df['Game_Id'] = game_id[-5:]
    game_df['Date'] = date

    return pd.DataFrame(game_df, columns=pbp_columns)


def combine_espn_html_pbp(html_df, espn_df, game_id, date, away_team, home_team):
    """
    Merge the coordinate from the espn feed into the html DataFrame
    
    :param html_df: DataFrame with info from html pbp
    :param espn_df: DataFrame with info from espn pbp
    :param game_id: json game id
    :param date: ex: 2016-10-24
    :param away_team: away team
    :param home_team: home team
    
    :return: merged DataFrame
    """
    if espn_df is not None:
        try:
            espn_df.period = espn_df.period.astype(int)
            df = pd.merge(html_df, espn_df, left_on=['Period', 'Seconds_Elapsed', 'Event'],
                          right_on=['period', 'time_elapsed', 'event'], how='left')

            df = df.drop(['period', 'time_elapsed', 'event'], axis=1)
        except Exception as e:
            print('Error for combining espn and html pbp for game {}'.format(game_id), e)
            return None
    else:
        df = html_df

    df['Game_Id'] = game_id[-5:]
    df['Date'] = date
    df['Away_Team'] = away_team
    df['Home_Team'] = home_team

    return pd.DataFrame(df, columns=pbp_columns)


def scrape_pbp(game_id, date, roster, game_json, players, teams):
    """
    Automatically scrapes the json and html, if the json is empty the html picks up some of the slack and the espn
    xml is also scraped for coordinates.
    
    :param game_id: json game id
    :param date: date of game
    :param roster: list of players in pre game roster
    :param game_json: json pbp for game
    :param players: dict of players
    :param teams: dict of teams
    
    :return: DataFrame with info or None if it fails
    """

    # Coordinates are only available in json from 2010 onwards
    if int(str(game_id)[:4]) >= 2010:
        json_df = json_pbp.parse_json(game_json, game_id)
        if json_df is None:
            return None   # Means there was an error parsing

        if_json = True if len(game_json['liveData']['plays']['allPlays']) > 0 else False
    else:
        if_json = False

    html_df = html_pbp.scrape_game(game_id, players, teams, if_json)
    if html_df is None:  # If None we couldn't get the html pbp
        return None

    # Check if the json is missing the plays...if it scrape ESPN for the coordinates
    if not if_json:
        espn_df = espn_pbp.scrape_game(date, teams['Home'], teams['Away'])
        game_df = combine_espn_html_pbp(html_df, espn_df, str(game_id), date, teams['Away'], teams['Home'])

        # Sometimes espn is corrupted so can't get coordinates
        if espn_df.empty:
            missing_coords.extend([[game_id, date]])

        # Because every game b4 2010 uses ESPN so no point in adding it in there
        if int(str(game_id)[:4]) >= 2010:
            espn_games.extend([[game_id, date]])
    else:
        game_df = combine_html_json_pbp(json_df, html_df, str(game_id), date)

    if game_df is not None:
        game_df['Home_Coach'] = roster['head_coaches']['Home']
        game_df['Away_Coach'] = roster['head_coaches']['Away']

    return game_df


def scrape_shifts(game_id, players, date):
    """
    Scrape the Shift charts (or TOI tables)
    
    :param game_id: json game id
    :param players: dict of players with numbers and id's
    :param date: date of game
    
    :return: DataFrame with info or None if it fails
    """
    shifts_df = None

    # Control for fact that shift json is only available from 2010 onwards
    if int(date[:4]) >= 2010:
        shifts_df = json_shifts.scrape_game(game_id)

    if shifts_df is None:
        shifts_df = html_shifts.scrape_game(game_id, players)

        if shifts_df is None:
            broken_shifts_games.extend([[game_id, date]])
            return None   # Both failed so just return nothing

    shifts_df['Date'] = date

    return shifts_df


def scrape_game(game_id, date, if_scrape_shifts):
    """
    This scrapes the info for the game.
    The pbp is automatically scraped, and the whether or not to scrape the shifts is left up to the user.
    
    :param game_id: game to scrap
    :param date: ex: 2016-10-24
    :param if_scrape_shifts: Boolean indicating whether to also scrape shifts 
    
    :return: DataFrame of pbp info
             (optional) DataFrame with shift info otherwise just None
    """
    print(' '.join(['Scraping Game ', game_id, date]))
    shifts_df = None

    roster = playing_roster.scrape_roster(game_id)
    game_json = json_pbp.get_pbp(game_id)           # Contains both player info (id's) and plays
    players, teams = get_teams_and_players(game_json, roster, game_id)

    # Game fails without any of these
    if not roster or not game_json or not teams or not players:
        broken_pbp_games.extend([[game_id, date]])
        broken_shifts_games.extend([[game_id, date]])
        return None, None

    pbp_df = scrape_pbp(game_id, date, roster, game_json, players, teams)

    if if_scrape_shifts and pbp_df is not None:
        shifts_df = scrape_shifts(game_id, players, date)

    if pbp_df is None:
        broken_pbp_games.extend([[game_id, date]])

    return pbp_df, shifts_df


def print_errors():
    """
    Print errors with scraping
    
    :return: None
    """
    global broken_shifts_games
    global broken_pbp_games
    global players_missing_ids
    global espn_games
    global missing_coords

    if broken_pbp_games:
        print('\nBroken pbp:')
        for x in broken_pbp_games:
            print(x[0], x[1])

    if broken_shifts_games:
        print('\nBroken shifts:')
        for x in broken_shifts_games:
            print(x[0], x[1])

    if players_missing_ids:
        print("\nPlayers missing ID's:")
        for x in players_missing_ids:
            print(x[0], x[1])

    if espn_games:
        print('\nESPN games:')
        for x in espn_games:
            print(x[0], x[1])

    if missing_coords:
        print('\nGames missing coordinates:')
        for x in missing_coords:
            print(x[0], x[1])

    print('\n')

    broken_shifts_games = []
    broken_pbp_games = []
    players_missing_ids = []
    espn_games = []
    missing_coords = []

