import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import json
import time

"""
Nikolai/Nikolay kulemin
"""


def return_name_html(info):
    """
    In the PBP html the name is in a format like: 'Center - MIKE RICHARDS'
    Some also have a hyphen in their last name so can't just split by '-'
    :param info: position and name
    :return: name
    """
    s=info.index('-')               # Find first hyphen
    return info[s + 1:].strip(' ')  # The name should be after the first hyphen


def get_players(json):
    """
    Return dict of players for that game
    :param json: gameData section of json
    :return: dict of players->keys are the name (in lowercase) and value is id
    """
    players={}

    players_json=json['players']
    for key in players_json.keys():
        players[players_json[key]['fullName'].upper()]=players_json[key]['id']

    return players


def shot_type(play_description):
    """
     Determine which zone the play occured in (unless one isn't listed)
    :param play_description: the type would be in here
    :return: the type if it's there (otherwise just NA)
    """
    types=['wrist', 'snap', 'slap', 'deflected', 'tip-in', 'backhand', 'wrap-around']

    play_description = [x.strip() for x in play_description.split(',')]      # Strip leading and trailing whitespace
    play_description = [i.lower() for i in play_description]                 # Convert to lowercase

    for t in types:
        if t in play_description:
            return t
    return 'NA'


def which_zone(play_description):
    """
    Determine which zone the play occurred in (unless one isn't listed)
    :param play_description: the zone would be included here
    :return: Off, Def, Neu, or NA
    """
    s=[x.strip() for x in play_description.split(',')]    # Split by comma's into a list
    zone=[x for x in s if 'Zone' in x]                    # Find if list contains which zone

    if not zone:
        return 'NA'

    if zone[0].find("Off") != -1:
        return 'Off'
    elif zone[0].find("Neu") != -1:
        return 'Neu'
    elif zone[0].find("Def") != -1:
        return 'Def'


def convert_to_seconds(minutes):
    """
    return minutes remaining in time format to seconds elapsed
    :param minutes: time remaining
    :return: time elapsed in seconds
    """
    import datetime

    # Check if the time format isn't correct (usually means nothing is there)
    try:
        x = time.strptime(minutes.split(',')[0], '%M:%S')
        return 1200-datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    except ValueError:
        return ' '


def clean_html_pbp(html):
    """
    Get rid of html and format the data
    :param html: the requested url
    :return: a list with all the info
    """
    pbp_html = BeautifulSoup(html.content, 'html.parser')
    td = pbp_html.select('td.+.bborder') + pbp_html.select('td.+.bborder+rborder')

    # Create a list of lists (each length 8)...corresponds to 8 columns in html pbp
    td = [td[i:i + 8] for i in range(0, len(td), 8)]

    for x in range(len(td)):
        for y in range(len(td[x])):

            # Get the 'br' tag for the time column...this get's us time remaining instead of elapsed and remaining combined
            if y==3:
                td[x][y]=td[x][y].find_all('br')[0].get_text()
            elif (y==6 or y==7) and td[x][0]!='#':
                # 6 & 7 These are the player one ice one's
                # The second statement controls for when it's just a header

                baz = td[x][y].find_all('td')
                bar = [baz[z] for z in range(len(baz)) if z%4!=0]  # Because of previous step we get repeats...so delete some

                # The setup in the list is now: Name/Number->Position->Blank...and repeat
                # Now strip all the html
                players=[]
                for i in range(len(bar)):
                    if i%3 == 0:
                        name=return_name_html(bar[i].find('font')['title'])
                        number=bar[i].get_text().strip('\n')  # Get number and strip leading/trailing endlines
                    elif i%3 == 1:
                        position=bar[i].get_text()
                        players.append([name, number, position])

                td[x][y]=players
            else:
                td[x][y]=td[x][y].get_text()

    return td


def getSchedule(year):
    """
    Given a year it returns the json for the schedule
    :param year: given year
    :return: raw json of schedule 
    """
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}-10-01&endDate={b}-06-20'.format(a=year, b=year+1)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Schedule for {} isn't there".format(year))

    schedule_json = json.loads(response.text)
    time.sleep(1)

    return schedule_json


def getPBP_json(game_id):
    """
    Given a game_id it returns the raw json
    :param game_id: the game
    :return: raw json of game
    """
    url = 'http://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Game {} for json isn't there".format(game_id))

    pbp_json = json.loads(response.text)
    time.sleep(1)

    return pbp_json


def getPBP_html(game_id):
    """
    Given a game_id it returns the raw html
    :param game_id: the game
    :return: raw html of game
    """
    game_id=str(game_id)
    url = 'http://www.nhl.com/scores/htmlreports/{}{}/PL{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Game {} for html isn't there".format(game_id))

    pbp_html=clean_html_pbp(response)

    return pbp_html


def scrapeSchedule(year):
    """
    Calls getSchedule and scrapes the raw schedule JSON
    :param year: year to scrape
    :return: list with all the game id's
    """
    schedule=[]

    schedule_json=getSchedule(year)
    for date in schedule_json['dates']:
        for game in date['games']:
            schedule.extend([game['gamePk']])

    return schedule


def parse_html_pbp(html, players):

    columns = ['Period', 'Seconds_Elapsed', 'Strength', 'Time_Remaining', 'Event', 'Description', 'Type', 'Ev_Zone',
               'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id','awayPlayer3', 'awayPlayer3_id',
               'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id',
               'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3', 'homePlayer3_id',
               'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6', 'homePlayer6_id',
               'Away_Goalie', 'Home_Goalie', 'Away_Skaters', 'Home_Skaters']

    df = pd.DataFrame(columns=columns)  # Create DataFrame for all game info

    for i in html:
        # Control for column headings
        if i[0]!='#':
            away_players=i[6]
            home_players=i[7]

            info_dict={}

            info_dict['Period']=i[1]
            info_dict['Event']=i[4]
            info_dict['Description']=i[5]

            # Populate away and home player info
            for j in range(6):
                try:
                    info_dict['awayPlayer{}'.format(j+1)]= away_players[j][0].upper()
                    info_dict['awayPlayer{}_id'.format(j + 1)] = players[away_players[j][0].upper()]
                except (KeyError, IndexError):
                    info_dict['awayPlayer{}'.format(j + 1)] = 'NA'
                    info_dict['awayPlayer{}_id'.format(j + 1)] = 'NA'

                try:
                    info_dict['homePlayer{}'.format(j+1)]= home_players[j][0].upper()
                    info_dict['homePlayer{}_id'.format(j + 1)] = players[home_players[j][0].upper()]
                except (KeyError, IndexError):
                    info_dict['homePlayer{}'.format(j + 1)] = 'NA'
                    info_dict['homePlayer{}_id'.format(j + 1)] = 'NA'

            # Did this because above method assumes goalie is at end of player list
            for x in away_players:
                if x[2]=='G':
                    info_dict['Away_Goalie']=x[0].upper()
                else:
                    info_dict['Away_Goalie'] = 'NA'

            for x in home_players:
                if x[2]=='G':
                    info_dict['Home_Goalie']=x[0].upper()
                else:
                    info_dict['Home_Goalie'] = 'NA'

            info_dict['Away_Skaters'] = len(away_players)
            info_dict['Home_Skaters'] = len(home_players)

            try:
                home_skaters = info_dict['Home_Skaters'] - 1 if info_dict['Home_Goalie'] != 'NA' else len(home_players)
                away_skaters = info_dict['Away_Skaters'] - 1 if info_dict['Away_Goalie'] != 'NA' else len(away_players)
            except KeyError:
                # Getting a key error here means that home/away goalie isn't there..which means home/away players are empty
                home_skaters=0
                away_skaters = 0

            info_dict['Strength'] = 'x'.join([str(home_skaters), str(away_skaters)])
            info_dict['Seconds_Elapsed']= convert_to_seconds(i[3])
            info_dict['Time_Remaining']=i[3]
            info_dict['Ev_Zone']= which_zone(info_dict['Description'])
            info_dict['Type']=shot_type(i[5])

            df = df.append(info_dict, ignore_index=True)

    return df

def parseEvent_json(event, home_team, away_team, columns):
    """
    Parses a single event when the info is in a json format
    :param event: json of event
    :param home_team: 
    :param away_team: 
    :param columns: list of columns in DataFrame
    :return: dictionary with the info
    """
    play=dict.fromkeys(columns, 'NA')

    play['Period'] = event['about']['period']
    play['Event'] = event['result']['eventTypeId']
    play['Description'] = event['result']['description']
    play['Time_Elapsed'] = event['about']['periodTime']
    play['Away_Team'] = away_team
    play['Home_Team'] = home_team
    play['Home_Score'] = event['about']['goals']['home']
    play['Away_Score'] = event['about']['goals']['away']

    # Check if an actual event occurred on the play
    if 'players' in event.keys():
        play['Ev_Team']=event['team']['triCode']

        play['p1_name']=event['players'][0]['player']['fullName']
        play['p1_ID'] = event['players'][0]['player']['id']

        for i in range(len(event['players'])):
            if event['players'][i]['playerType'] != 'Goalie':
                play['p{}_name'.format(i+1)] = event['players'][i]['player']['fullName']
                play['p{}_ID'.format(i+1)] = event['players'][i]['player']['id']
            else:
                play['Away_Goalie'] = event['players'][i]['player']['fullName'] if play['Ev_Team']==home_team else 'NA'
                play['Home_Goalie'] = event['players'][i]['player']['fullName'] if play['Ev_Team']==away_team else 'NA'

        # If it's a penalty include the type->minor/double/major...etc
        if play['Event']=='PENALTY':
            play['Type'] = event['result']['secondaryType']+'-'+event['result']['penaltySeverity']
        else:
            try:
                play['Type'] = event['result']['secondaryType']     # Events like Faceoffs don't have secondaryType's
            except KeyError:
                play['Type']='NA'

        # Coordinates aren't always there
        try:
            play['xC'] = event['coordinates']['x']
            play['yC'] = event['coordinates']['y']
        except KeyError:
            play['xC'] = 'Na'
            play['yC'] = 'Na'

    # NHL has Ev_Team for blocked shot as team who blocked it...flip it
    if play['Event'] == 'BLOCKED_SHOT':
        play['Ev_Team']= away_team if play['Ev_Team']==home_team else home_team

    # Sometimes they record events for shots in the wrong zone...so change it
    if play['Event'] == 'MISS' or play['Event'] == 'SHOT' or play['Event'] == 'GOAL' or play['Event'] == 'BLOCK':

        if play['Ev_Team'] == home_team:
            # X should be negative in 1st and 3rd for home_team
            if (play['Period']==1 or play['Period'] == 3) and play['xC']>0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
            elif play['Period'] == 2 and play['xC']<0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
        else:
            # X should be positive in 1st and 3rd for away_team
            if (play['Period'] == 1 or play['Period'] == 3) and play['xC'] < 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
            elif play['Period'] == 2 and play['xC'] > 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])

    return play


def scrapeGame(game_id):
    """
    Calls getPBP and scrapes the raw PBP json and HTML
    :param game_id: game to scrape
    :return: DataFrame of game info
    """
    columns=['Period', 'Event', 'Description', 'Date', 'Game_ID', 'Ev_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID',
             'p3_name', 'p3_ID', 'Ev_Zone', 'Type', 'Away_Team', 'Home_Team', 'Away_Goalie', 'Home_Goalie',
             'Away_Score', 'Home_Score',  'xC', 'yC', 'Home_Zone']

    game_json=getPBP_json(game_id)  # Get json PBP
    game_html=getPBP_html(game_id)  # Get html PBP

    game_df=pd.DataFrame(columns=columns)  # Create DataFrame for all game info

    away_team=game_json['gameData']['teams']['away']['triCode']
    home_team=game_json['gameData']['teams']['home']['triCode']
    date=game_json['gameData']['datetime']['dateTime']

    # Go through plays in json PBP and fill in DataFrame
    plays=game_json['liveData']['plays']['allPlays'][2:]
    for play in plays:
        if play['result']['eventTypeId']!='PERIOD_READY' and play['result']['eventTypeId']!='PERIOD_OFFICIAL':
            game_df=game_df.append(parseEvent_json(play, home_team, away_team, columns), ignore_index=True)

    # Go through html PBP
    html_df=parse_html_pbp(game_html, get_players(game_json['gameData']))

    game_df['Date']=date[:10]
    game_df['Game_ID']=game_id

    game_df=join_html_json_pbp(game_df, html_df)

    return game_df

def join_html_json_pbp(json, html):

    """
    Join both data sources
    # Home_Zone->Need to do this eventually
    :param json: json pbp DataFrame
    :param html: html pbp DataFrame
    :return: finished pbp
    """
    # json.ix[json.Event == BLOCKED_SHOT', 'Event'] = 'BLOCK'
    # json.ix[json.Event == 'MISSED_SHOT', 'Event'] = 'MISS'

    # Check if same amount of events
    if json.shape[0]!=html.shape[0]:
        return False

    # Drop from json pbp
    json = json.drop('Event', axis=1)
    json = json.drop('Away_Goalie', axis=1)
    json = json.drop('Home_Goalie', axis=1)
    json = json.drop('Ev_Zone', axis=1)

    # Drop from html pbp
    html = html.drop('Time_Remaining', axis=1)
    html = html.drop('Period', axis=1)
    html = html.drop('Type', axis=1)
    html = html.drop('Description', axis=1)

    game_df=html       # It's easier if I just start off with html as the final

    # Add all relevant columns in json to game_df (which is just html)
    # Little clunky...but I wanted to put certain columns in certain spots
    game_df.insert(0, 'Time_Elapsed', json['Time_Elapsed'])
    game_df.insert(0, 'Description', json['Description'])
    game_df.insert(0, 'Period', json['Period'])
    game_df.insert(0, 'Date', json['Date'])
    game_df.insert(0, 'Game_ID', json['Game_ID'])
    game_df.insert(8, 'Type', json['Type'])
    game_df.insert(9, 'Ev_Team', json['Ev_Team'])
    game_df.insert(10, 'Away_Team', json['Away_Team'])
    game_df.insert(11, 'Home_Team', json['Home_Team'])
    game_df.insert(13, 'p1_name', json['p1_name'])
    game_df.insert(14, 'p1_ID', json['p1_ID'])
    game_df.insert(15, 'p2_name', json['p2_name'])
    game_df.insert(16, 'p2_ID', json['p2_ID'])
    game_df.insert(17, 'p3_name', json['p3_name'])
    game_df.insert(18, 'p3_ID', json['p3_ID'])
    game_df.insert(47, 'Away_Score', json['Away_Score'])
    game_df.insert(48, 'Home_Score', json['Home_Score'])
    game_df.insert(49, 'xC', json['xC'])
    game_df.insert(50, 'yC', json['yC'])

    return game_df


def scrapeYear(year):
    """
    Calls scrapeSchedule to get the game_id's to scrape and then calls scrapeGame and combines
    all the scraped games into one DataFrame
    :param year: year to scrape
    :return: 
    """
    schedule=scrapeSchedule(year)
    season_df=pd.DataFrame()

    for game in schedule:
        season_df=season_df.append(scrapeGame(game))

"""TESTS"""
#foo=scrapeGame(2016020001)
#foo.to_csv('bar.csv', sep=',')


