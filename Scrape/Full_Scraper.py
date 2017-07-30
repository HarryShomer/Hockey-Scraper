import json_pbp
import html_pbp
import espn_pbp
import json_shifts
import html_shifts
import playing_roster
import season_schedule
import pandas as pd
import shared
import time


# Holds list for broken games for shifts and pbp
broken_shifts_games = []
broken_pbp_games = []
players_missing_ids = []
espn_games = []


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
            print(name, ' is missing an ID number')
            players[name]['id'] = 'NA'

    return players


def combine_players_lists(json_players, roster_players, game_id):
    """
    Combine the json list of players (which contains id's) with the list in the roster html
    :param json_players: dict of all players with id's
    :param roster_players: dict with home and and away keys for players
    :param game_id:
    :return: dict containing home and away keys -> which contains list of info on each player
    """
    home_players = dict()
    for player in roster_players['Home']:
        try:
            name = shared.fix_name(player[2])
            id = json_players[name]['id']
            home_players[name] = {'id': id, 'number': player[0]}
        except KeyError:
            # This usually means it's the backup goalie (who didn't play) so it's no big deal with them
            if player[1] != 'G':
                players_missing_ids.extend([player, game_id])
                home_players[name] = {'id': 'NA', 'number': player[0]}

    away_players = dict()
    for player in roster_players['Away']:
        try:
            name = shared.fix_name(player[2])
            id = json_players[name]['id']
            away_players[name] = {'id': id, 'number': player[0]}
        except KeyError:
            if player[1] != 'G':
                players_missing_ids.extend([player, game_id])
                away_players[name] = {'id': 'NA', 'number': player[0]}

    return {'Home': home_players, 'Away': away_players}


def combine_html_json_pbp(json_df, html_df, game_id, date):
    """
    Join both data sources
    :param json_df: json pbp DataFrame
    :param html_df: html pbp DataFrame
    :param game_id:
    :param date:
    :return: finished pbp
    
    Add game_id and date
    Get rid of period, event, time_elapsed
    """
    columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
               'Ev_Zone', 'Type', 'Ev_Team', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
               'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
               'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
               'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
               'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
               'homePlayer6_id', 'Away_Goalie', 'Home_Goalie',  'Away_Skaters', 'Home_Skaters', 'Away_Score',
               'Home_Score', 'xC', 'yC']

    try:
        html_df.Period = html_df.Period.astype(int)
        game_df = pd.merge(html_df, json_df, left_on=['Period', 'Event', 'Seconds_Elapsed'],
                           right_on=['period', 'event', 'seconds_elapsed'], how='left')

        # This id because merge doesn't work well with shootouts
        game_df = game_df.drop_duplicates(subset=['Period', 'Event', 'Description', 'Seconds_Elapsed'])

        game_df['Game_Id'] = game_id[-5:]
        game_df['Date'] = date
        return pd.DataFrame(game_df, columns=columns)
    except Exception as e:
        print('Problem combining Html Json pbp for game {}'.format(game_id, e))


def combine_espn_html_pbp(html_df, espn_df, game_id, date, away_team, home_team):
    """
    Merge the coordinate from the espn feed into the html DataFrame
    :param html_df: dataframe with info from html pbp
    :param espn_df: dataframe with info from espn pbp
    :param game_id: json game id
    :param date: ex: 2016-10-24
    :param away_team:
    :param home_team
    :return: merged DataFrame
    """
    columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
               'Ev_Zone', 'Type', 'Ev_Team', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
               'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
               'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
               'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
               'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
               'homePlayer6_id', 'Away_Goalie', 'Home_Goalie', 'Away_Skaters', 'Home_Skaters', 'Away_Score',
               'Home_Score', 'xC', 'yC']

    espn_df.period = espn_df.period.astype(int)
    html_df.to_csv('baz.csv', sep=',')
    espn_df.to_csv('bar.csv', sep=',')
    try:
        df = pd.merge(html_df, espn_df, left_on=['Period', 'Seconds_Elapsed', 'Event'],
                      right_on=['period', 'time_elapsed', 'event'], how='left')

        # df = df.drop_duplicates(subset=['Period', 'Event', 'Seconds_Elapsed'])
        df = df.drop(['period', 'time_elapsed', 'event'], axis=1)
    except Exception as e:
        print('Error for combining espn and html pbp for game {}'.format(game_id), e)
        return None

    df['Game_Id'] = game_id[-5:]
    df['Date'] = date
    df['Away_Team'] = away_team
    df['Home_Team'] = home_team

    return pd.DataFrame(df, columns=columns)


def scrape_pbp(game_id, date, roster):
    """
    Scrapes the pbp
    Automatically scrapes the json and html, if the json is empty the html picks up some of the slack and the espn
    xml is also scraped for coordinates
    :param game_id: json game id
    :param date: 
    :param roster: list of players in pre game roster
    :return: DataFrame with info or None if it fails
             dict of players with id's and numbers
    """
    try:
        game_json = json_pbp.get_pbp(game_id)
        teams = json_pbp.get_teams(game_json)                           # Get teams from json
        player_ids = get_players_json(game_json['gameData'])
        players = combine_players_lists(player_ids, roster['players'], game_id)  # Combine roster names with player id's
    except Exception as e:
        print('Problem with getting the teams or players', e)
        return None, None

    try:
        json_df = json_pbp.parse_json(game_json)
    except Exception as e:
        print('Error for Json pbp for game {}'.format(game_id), e)
        return None, None

    # Check if the json is missing the plays...if it is enable the HTML parsing to do more work to make up for the
    # json and scrape ESPN for the coordinates
    if len(game_json['liveData']['plays']['allPlays']) == 0:
        espn_games.extend([game_id])
        html_df = html_pbp.scrape_game(game_id, players, teams, False)
        espn_df = espn_pbp.scrape_game(date, teams['Home'], teams['Away'])
        game_df = combine_espn_html_pbp(html_df, espn_df, str(game_id), date, teams['Away'], teams['Home'])
    else:
        html_df = html_pbp.scrape_game(game_id, players, teams, True)
        game_df = combine_html_json_pbp(json_df, html_df, str(game_id), date)

    if game_df is not None:
        game_df['Home_Coach'] = roster['head_coaches']['Home']
        game_df['Away_Coach'] = roster['head_coaches']['Away']

    return game_df, players


def scrape_shifts(game_id, players):
    """
    Scrape the Shift charts (or TOI tables)
    :param game_id: json game id
    :param players: dict of players with numbers and id's
    :return: DataFrame with info or None if it fails
    """
    try:
        shifts_df = json_shifts.scrape_game(game_id)
    except Exception as e:
        print('Error for Json shifts for game {}'.format(game_id), e)
        try:
            shifts_df = html_shifts.scrape_game(game_id, players)
        except Exception as e:
                broken_shifts_games.extend([game_id])
                print('Error for html shifts for game {}'.format(game_id), e)
                return None

    return shifts_df


def scrape_game(game_id, date, if_scrape_shifts):
    """
    This scrapes the info for the game.
    The pbp is automatically scraped, and the whether or not to scrape the shifts is left up to the user
    :param game_id: game to scrap
    :param date: ex: 2016-10-24
    :param if_scrape_shifts: boolean, check if scrape shifts
    :return: DataFrame of pbp info
             (optional) DataFrame with shift info
    """
    shifts_df = None

    try:
        roster = playing_roster.scrape_roster(game_id)
    except Exception:
        broken_pbp_games.extend([game_id, date])
        return None, None     # Everything fails without the roster

    pbp_df, players = scrape_pbp(game_id, date, roster)

    if pbp_df is None:
        broken_pbp_games.extend([game_id, date])

    if if_scrape_shifts and pbp_df is not None:
        shifts_df = scrape_shifts(game_id, players)

    return pbp_df, shifts_df


def scrape_year(year, if_scrape_shifts):
    """
    Calls scrapeSchedule to get the game_id's to scrape and then calls scrapeGame and combines
    all the scraped games into one DataFrame
    :param year: year to scrape
    :param if_scrape_shifts: boolean, check if scrape shifts
    :return: nothing
    
    0-1-2-3-4-5-6-7-8-9
    x[i+4]
    """
    schedule = season_schedule.scrape_schedule(year)

    foo = []
    bar = []
    for game in schedule:
        print(game)
        pbp_df, shifts_df = scrape_game(game[0], game[1], if_scrape_shifts)
        if pbp_df is not None:
            foo.extend([pbp_df])
        if shifts_df is not None:
            bar.extend([shifts_df])

    season_pbp_df = pd.concat(foo)
    season_pbp_df = season_pbp_df.reset_index(drop=True)
    season_pbp_df.to_csv('nhl_pbp{}{}.csv'.format(year, int(year)+1), sep=',')
    if if_scrape_shifts:
        season_shifts_df = pd.concat(bar)
        season_shifts_df = season_shifts_df.reset_index(drop=True)
        season_shifts_df.to_csv('nhl_shifts{}{}.csv'.format(year, int(year)+1), sep=',')

scrape_year(2016, False)

"""Test
scrape_year(2010, False)

print('Broken pbp:')
for x in broken_pbp_games:
    print(x)

print('Broken shifts:')
for x in broken_shifts_games:
    print(x)

print('Missing ids')
for x in players_missing_ids:
    print(x)
"""




