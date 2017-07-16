import json_pbp
import html_pbp
import espn_pbp
import json_shifts
import html_shifts
import playing_roster
import season_schedule
import pandas as pd
import requests
import json
import time


"""
Parentuea-> PA vs pierre alexander
Kulemin-> nikolay vs nikoli
Max Talbot...Maxime
Zachary Sanford->Zach

"""


def get_players_json(json):
    """
    Return dict of players for that game
    :param json: gameData section of json
    :return: dict of players->keys are the name (in uppercase)  
    """
    players = dict()

    players_json = json['players']
    for key in players_json.keys():
        players[players_json[key]['fullName'].upper()] = {'id': ' '}
        try:
            players[players_json[key]['fullName'].upper()]['id'] = players_json[key]['id']
        except KeyError:
            print(players_json[key]['fullName'].upper(), ' is missing an ID number')
            players[players_json[key]['fullName'].upper()]['id'] = 'NA'

    return players


def combine_players_lists(json_players, roster_players):
    """
    Combine the json list of players (which contains id's) with the list in the roster html
    :param json_players: dict of all players with id's
    :param roster_players: dict with home and and away keys for players
    :return: dict containing home and away keys -> which contains list of info on each player
    """
    home_players=dict()
    for player in roster_players['Home']:
        try:
            id = json_players[player[2]]['id']
            home_players[player[2]] = {'id': id, 'number': player[0]}
        except KeyError:
            # This usually means it's the backup goalie (who didn't play) so it's no big deal
            print('{} is missing an id number'.format(player[2]))
            home_players[player[2]] = {'id': 'NA', 'number': player[0]}

    away_players = dict()
    for player in roster_players['Away']:
        try:
            id = json_players[player[2]]['id']
            away_players[player[2]] = {'id': id, 'number': player[0]}
        except KeyError:
            print('{} is missing an id number'.format(player[2]))
            away_players[player[2]] = {'id': 'NA', 'number': player[0]}

    return {'Home': home_players, 'Away': away_players}


def combine_html_json_pbp(json_df, html_df):
    """
    Join both data sources
    :param json_df: json pbp DataFrame
    :param html_df: html pbp DataFrame
    :return: finished pbp
    """
    columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
               'Ev_Zone', 'Type', 'Ev_Team', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
               'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
               'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
               'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
               'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
               'homePlayer6_id', 'Away_Goalie', 'Home_Goalie', 'Away_Score', 'Home_Score', 'xC', 'yC']

    # Check if same amount of events...if not something is wrong
    if json_df.shape[0] != html_df.shape[0]:
        print('The Html and Json pbp for game {} are not the same'.format(json_df['Game_Id']))
        return None
    else:
        json_df = json_df.drop('Event', axis=1)       # Drop from json pbp

        game_df = pd.concat([html_df, json_df], axis=1)
        game_df = game_df[columns]   # Make the columns in the order specified above

        return game_df


def combine_espn_html_pbp(html_df, espn_df):
    """
    Merge the coordinate from the espn feed into the html DataFrame
    :param html_df: 
    :param espn_df: 
    :return: merged DataFrame
    """
    columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength',
               'Ev_Zone', 'Type', 'Ev_Team', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
               'p3_name', 'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3',
               'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6',
               'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3',
               'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6',
               'homePlayer6_id', 'Away_Goalie', 'Home_Goalie', 'Away_Score', 'Home_Score', 'xC', 'yC']

    """
    if html_df.shape[0] != espn_df.shape[0]:
        print('The Html and Espn pbp are not the same')
        return None

    return pd.concat([html_df, espn_df], axis=1)
    """
    df = pd.merge(html_df, espn_df, left_on=['Period', 'Seconds_Elapsed', 'Event'], right_on=['period', 'time_elapsed', 'event'],
                  how='left')
    return df.drop(['period', 'time_elapsed', 'event'], axis=1)


def scrapeGame(game_id, date):
    """
    
    
    
    :param game_id: game to scrap
    :param date: ex: 2016-10-24
    :return: DataFrame of game info
    """

    try:
        roster = playing_roster.scrape_roster(game_id)
    except Exception:
        print('Problem with playing roster for game {}'.format(game_id))

    try:
        game_json = json_pbp.get_pbp(game_id)
    except requests.exceptions.HTTPError as e:
        print('Json pbp for game {} is not there'.format(game_id), e)
        return None

    teams = json_pbp.get_teams(game_json)    # Get teams from json

    player_ids = get_players_json(game_json['gameData'])
    players = combine_players_lists(player_ids, roster['players'])

    try:
        game_html = html_pbp.get_pbp(game_id)
    except requests.exceptions.HTTPError as e:
        print('Html pbp for game {} is not there'.format(game_id), e)
        return None

    try:
        json_df = json_pbp.parse_json(game_json, game_id)
    except Exception as e:
        print('Error for Json pbp for game {}'.format(game_id), e)
        return None

    try:
        # Check if the json is missing the plays...if it is enable the HTML parsing to do more work to make up for the
        # json and scrape ESPN for the coordinates
        #if len(game_json['liveData']['plays']['allPlays']) == 0:
        s=0
        if s==0:
            s=9
        else:
            html_df = html_pbp.parse_html(html_pbp.clean_html_pbp(game_html), players, teams['Home'], teams['Away'], True)
            game_df = combine_html_json_pbp(json_df, html_df)
    except Exception as e:
        print('Error for html pbp for game {}'.format(game_id), e)
        return None
    html_df = html_pbp.parse_html(html_pbp.clean_html_pbp(game_html), players, teams['Home'], teams['Away'], False)
    espn_df = espn_pbp.get_espn(json_df['Date'][0], teams['Home'], teams['Away'])
    game_df = combine_espn_html_pbp(html_df, espn_df)

    """
    try:
        shifts_df = json_shifts.scrape_game(game_id)
    except Exception as e:
        print('Error for Json shifts for game {}'.format(game_id), e)
        try:
            shifts_df = html_shifts.scrape_game(game_id, players)
        except Exception as e:
                print('Error for html shifts for game {}'.format(game_id), e)
    """

    game_df.to_csv('bar.csv', sep=',')

    return game_df


def scrape_year(year):
    """
    Redefining how scrapeYear is in both the shift and PBP

    Calls scrapeSchedule to get the game_id's to scrape and then calls scrapeGame and combines
    all the scraped games into one DataFrame
    :param year: year to scrape
    :return: 
    """
    schedule = season_schedule.scrape_schedule(year)
    season_pbp_df = pd.DataFrame()
    season_shift_df = pd.DataFrame()

    for game in schedule:
        frames = scrapeGame(game[0], game[1])

        if frames[0] is not None:
            season_pbp_df = season_pbp_df.append(frames[0])
        if frames[1] is not None:
            season_shift_df = season_shift_df.append(frames[1])


"""Test"""

start = time.time()

print(20001)
scrapeGame(2016020894, '')
"""
print(20002)
scrapeGame(2011020002)
print(20003)
scrapeGame(2012020003)
print(20004)
scrapeGame(2013020004)
print(20005)
scrapeGame(2014020005)
print(20006)
scrapeGame(2015020006)
print(20007)
scrapeGame(2016020007)
"""

end = time.time()
print((end-start)/7)




