"""
This module contains code to scrape data for a single game
"""

import pandas as pd

import hockey_scraper.nhl.pbp.espn_pbp as espn_pbp
import hockey_scraper.nhl.pbp.html_pbp as html_pbp
import hockey_scraper.nhl.pbp.json_pbp as json_pbp
import hockey_scraper.nhl.playing_roster as playing_roster
import hockey_scraper.nhl.shifts.html_shifts as html_shifts
import hockey_scraper.nhl.shifts.json_shifts as json_shifts
import hockey_scraper.utils.shared as shared

broken_shifts_games = []
broken_pbp_games = []
players_missing_ids = []
missing_coords = []


pbp_columns = [
    'Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
    'Ev_Zone', 'Type', 'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
    'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
    'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
    'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
    'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
    'homePlayer6_id',  'Away_Players', 'Home_Players', 'Away_Score', 'Home_Score', 'Away_Goalie',
    'Away_Goalie_Id', 'Home_Goalie', 'Home_Goalie_Id', 'xC', 'yC', 'Home_Coach', 'Away_Coach'
]


def check_goalie(row):
    """
    Checks for bad goalie names (you can tell by them having no player id)
    
    :param row: df row
    
    :return: None
    """
    if row['Away_Goalie'] != '' and row['Away_Goalie_Id'] is None:
        if [row['Away_Goalie'], row['Game_Id']] not in players_missing_ids:
            players_missing_ids.extend([[row['Away_Goalie'], row['Game_Id']]])

    if row['Home_Goalie'] != '' and row['Home_Goalie_Id'] is None:
        if [row['Home_Goalie'], row['Game_Id']] not in players_missing_ids:
            players_missing_ids.extend([[row['Home_Goalie'], row['Game_Id']]])


def get_players_json(game_json):
    """
    Return dict of players for that game by team

    :param players_json: players section of json

    :return: {team -> players}
    """
    players = {"home": {}, "away": {}}

    for venue in players:
        team_players = game_json['liveData']['boxscore']['teams'][venue]['players']
        team_name = shared.get_team(game_json['liveData']['boxscore']['teams'][venue]['team']['name'])

        for id_key in team_players: 
            player_name = shared.fix_name(team_players[id_key]['person']['fullName'])

            players[venue][player_name] = {
                "id": team_players[id_key]['person']['id'], 
                "last_name": game_json['gameData']['players'][id_key]['lastName'].upper()
            }

    return players


# TODO: Assumes no two players on the same team can have the same name
#       Could potentially differentiate by number or position
def combine_players_lists(json_players, roster_players, game_id):
    """
    Combine the json list of players (which contains id's) with the list in the roster html

    :param json_players: dict of all players with id's
    :param roster_players: dict with home and and away keys for players
    :param game_id: id of game

    :return: dict containing home and away keys -> which contains list of info on each player
    """
    players = {'Home': dict(), 'Away': dict()}

    for venue in players:
        for player in roster_players[venue]:
            try:
                name = shared.fix_name(player[2])
                player_id = json_players[venue.lower()][name]['id']
                players[venue][name] = {'id': player_id, 'number': player[0], 'last_name': json_players[venue.lower()][name]['last_name']}
            except KeyError as e:
                # If he was listed as a scratch and not a goalie (check_goalie deals with goalies)
                # As a whole the scratch list shouldn't be trusted but if a player is missing an id # and is on the
                # scratch list I'm willing to assume that he didn't play
                if not player[3] and player[1] != 'G':
                    player.extend([game_id])
                    players_missing_ids.extend([[player[2], player[4]]])
                    players[venue][name] = {'id': None, 'number': player[0], 'last_name': ''}

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
        player_ids = get_players_json(game_json)
        players = combine_players_lists(player_ids, roster['players'], game_id)
    except Exception as e:
        shared.print_error('Problem with getting the teams or players')
        return None, None

    return players, teams


def combine_html_json_pbp(json_df, html_df, game_id, date):
    """
    Join both data sources. First try merging on event id (which is the DataFrame index) if both DataFrames have the
    same number of rows. If they don't have the same number of rows, merge on: Period', Event, Seconds_Elapsed, p1_ID. 
    
    :param json_df: json pbp DataFrame
    :param html_df: html pbp DataFrame
    :param game_id: id of game
    :param date: date of game
    
    :return: finished pbp
    """
    # Don't need those columns to merge in
    json_df = json_df.drop(['p1_name', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID'], axis=1)

    try:
        # If they aren't equal it's usually due to the HTML containing a challenge event
        if html_df.shape[0] == json_df.shape[0]:
            json_df = json_df[['period', 'event', 'seconds_elapsed', 'xC', 'yC']]
            game_df = pd.merge(html_df, json_df, left_index=True, right_index=True, how='left')
        else:
            # We always merge if they aren't equal but we check if it's due to a challenge so we can print out a better
            # warning message for the user.
            # NOTE: May be slightly incorrect. It's possible for there to be a challenge and another issue for one game.
            if 'CHL' in list(html_df.Event):
                shared.print_warning("The number of rows in the Html and Json pbp are different because the"
                                     " Json pbp, for some reason, does not include challenges. Will instead merge on "
                                     "Period, Event, Time, and p1_id.")
            else:
                shared.print_warning("The number of rows in the Html and json pbp are different because "
                                     "someone fucked up. Will instead merge on Period, Event, Time, and p1_id.")

            # Actual Merging
            game_df = pd.merge(html_df, json_df, left_on=['Period', 'Event', 'Seconds_Elapsed', 'p1_ID'],
                               right_on=['period', 'event', 'seconds_elapsed', 'p1_ID'], how='left')

        # This is always done - because merge doesn't work well with shootouts
        game_df = game_df.drop_duplicates(subset=['Period', 'Event', 'Description', 'Seconds_Elapsed'])
    except Exception as e:
        shared.print_error('Problem combining Html Json pbp for game {}'.format(game_id))
        return

    game_df['Game_Id'] = game_id[-5:]
    game_df['Date'] = date

    return pd.DataFrame(game_df, columns=pbp_columns)


def combine_espn_html_pbp(html_df, espn_df, game_id, date, away_team, home_team):
    """
    Merge the coordinate from the espn feed into the html DataFrame
    
    Can't join here on event_id because the plays are often out of order and pre-2009 are often missing events. 
    
    :param html_df: DataFrame with info from html pbp
    :param espn_df: DataFrame with info from espn pbp
    :param game_id: json game id
    :param date: ex: 2016-10-24
    :param away_team: away team
    :param home_team: home team
    
    :return: merged DataFrame
    """
    if espn_df is not None and not espn_df.empty:
        try:
            game_df = pd.merge(html_df, espn_df, left_on=['Period', 'Seconds_Elapsed', 'Event'],
                               right_on=['period', 'time_elapsed', 'event'], how='left')

            # Shit happens
            game_df = game_df.drop_duplicates(subset=['Period', 'Event', 'Description', 'Seconds_Elapsed'])

            df = game_df.drop(['period', 'time_elapsed', 'event'], axis=1)
        except Exception as e:
            shared.print_error('Error combining espn and html pbp for game {}'.format(game_id))
            return None
    else:
        df = html_df

    df['Game_Id'] = game_id[-5:]
    df['Date'] = date
    df['Away_Team'] = away_team
    df['Home_Team'] = home_team

    return pd.DataFrame(df, columns=pbp_columns)


def scrape_pbp_live(game_id, date, roster, game_json, players, teams, espn_id=None):
    """
    Wrapper for scraping the live pbp

    :param game_id: json game id
    :param date: date of game
    :param roster: list of players in pre game roster
    :param game_json: json pbp for game
    :param players: dict of players
    :param teams: dict of teams
    :param espn_id: Game Id for the espn game. Only provided when live scraping

    :return: Tuple - pbp & status
    """
    html_df, status = html_pbp.scrape_game_live(game_id, players, teams)
    game_df = scrape_pbp(game_id, date, roster, game_json, players, teams, espn_id=espn_id, html_df=html_df)
    return game_df, status


def scrape_pbp(game_id, date, roster, game_json, players, teams, espn_id=None, html_df=None):
    """
    Scrape the Pbp info. The HTML is always scraped.

    The Json is parse whe season >= 2010 and there are plays. Otherwise ESPN is gotten to supplement
    the HTML with coordinate.

    The espn_id and the html data can be fed as keyword argument to speed up execution. This is used by
    the live game scraping class.

    :param game_id: json game id
    :param date: date of game
    :param roster: list of players in pre game roster
    :param game_json: json pbp for game
    :param players: dict of players
    :param teams: dict of teams
    :param espn_id: Game Id for the espn game. Only provided when live scraping
    :param html_df: Can provide DataFrame for html. Only done for live-scraping

    :return: DataFrame with info or None if it fails
    """
    # Coordinates are only available in json from 2010 onwards
    if int(str(game_id)[:4]) >= 2010 and len(game_json['liveData']['plays']['allPlays']) > 0:
        json_df = json_pbp.parse_json(game_json, game_id)
    else:
        json_df = None

    # For live sometimes the json lags the html so if given we don't bother
    if not isinstance(html_df, pd.DataFrame):
        html_df = html_pbp.scrape_game(game_id, players, teams)

    if html_df is None or html_df.empty:
        return None

    # Check if the json is missing the plays...if it is scrape ESPN for the coordinates
    if json_df is None or json_df.empty:
        espn_df = espn_pbp.scrape_game(date, teams['Home'], teams['Away'], game_id=espn_id)
        game_df = combine_espn_html_pbp(html_df, espn_df, str(game_id), date, teams['Away'], teams['Home'])

        # Sometimes espn is corrupted so can't get coordinates
        if espn_df is None or espn_df.empty:
            missing_coords.extend([[game_id, date]])
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
    if shared.get_season(date) >= 2010:
        shifts_df = json_shifts.scrape_game(game_id)

    if shifts_df is None or shifts_df.empty:
        shifts_df = html_shifts.scrape_game(game_id, players)

        if shifts_df is None or shifts_df.empty:
            shared.print_error("Unable to scrape shifts for game " + game_id)
            broken_shifts_games.extend([[game_id, date]])
            return None

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
        if if_scrape_shifts:
            broken_shifts_games.extend([[game_id, date]])

        return None, None

    pbp_df = scrape_pbp(game_id, date, roster, game_json, players, teams)

    # Only scrape shifts if asked and pbp is good
    if if_scrape_shifts and pbp_df is not None:
        shifts_df = scrape_shifts(game_id, players, date)

    if pbp_df is None:
        broken_pbp_games.extend([[game_id, date]])

    return pbp_df, shifts_df
