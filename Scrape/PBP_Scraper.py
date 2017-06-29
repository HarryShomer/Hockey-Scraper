import pandas as pd
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
    Determine which zone the play occurred in (unless one isn't listed)
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

    # Check if the time format isn't correct (can happen in html...usually means nothing is there)
    try:
        x = time.strptime(minutes.split(',')[0], '%M:%S')
        return datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    except ValueError:
        return ' '


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


def strip_html_pbp(td):
    """
    Strip html tags and such 
    :param td: pbp
    :return: list of plays (which contain a list of info) stripped of html
    """
    for y in range(len(td)):
        # Get the 'br' tag for the time column...this get's us time remaining instead of elapsed and remaining combined
        if y == 3:
            td[y] = td[y].find_all('br')[0].get_text()
        elif (y == 6 or y == 7) and td[0]!= '#':
            # 6 & 7 These are the player one ice one's
            # The second statement controls for when it's just a header

            baz = td[y].find_all('td')
            bar = [baz[z] for z in range(len(baz)) if z % 4 != 0]  # Because of previous step we get repeats...so delete some

            # The setup in the list is now: Name/Number->Position->Blank...and repeat
            # Now strip all the html
            players = []
            for i in range(len(bar)):
                if i % 3 == 0:
                    name = return_name_html(bar[i].find('font')['title'])
                    number = bar[i].get_text().strip('\n')  # Get number and strip leading/trailing endlines
                elif i % 3 == 1:
                    position = bar[i].get_text()
                    players.append([name, number, position])

            td[y]= players
        else:
            td[y]= td[y].get_text()

    return td


def clean_html_pbp(html):
    """
    Get rid of html and format the data
    :param html: the requested url
    :return: a list with all the info
    """
    soup = BeautifulSoup(html.content, 'html.parser')
    td = soup.select('td.+.bborder')

    # Create a list of lists (each length 8)...corresponds to 8 columns in html pbp
    td = [td[i:i + 8] for i in range(0, len(td), 8)]

    cleaned_html = [strip_html_pbp(x) for x in td]

    return cleaned_html


def parseEvent_html(event, players):
    """
    Receievs an event and parses it
    :param event: 
    :param players: players in game
    :return: dict with info
    """

    away_players = event[6]
    home_players = event[7]

    info_dict = dict()

    info_dict['Period'] = event[1]
    info_dict['Event'] = event[4]
    info_dict['Description'] = event[5]

    # Populate away and home player info
    for j in range(6):
        try:
            info_dict['awayPlayer{}'.format(j + 1)] = away_players[j][0].upper()
            info_dict['awayPlayer{}_id'.format(j + 1)] = players[away_players[j][0].upper()]
        except (KeyError, IndexError):
            info_dict['awayPlayer{}'.format(j + 1)] = 'NA'
            info_dict['awayPlayer{}_id'.format(j + 1)] = 'NA'

        try:
            info_dict['homePlayer{}'.format(j + 1)] = home_players[j][0].upper()
            info_dict['homePlayer{}_id'.format(j + 1)] = players[home_players[j][0].upper()]
        except (KeyError, IndexError):
            info_dict['homePlayer{}'.format(j + 1)] = 'NA'
            info_dict['homePlayer{}_id'.format(j + 1)] = 'NA'

    # Did this because above method assumes goalie is at end of player list
    for x in away_players:
        if x[2] == 'G':
            info_dict['Away_Goalie'] = x[0].upper()
        else:
            info_dict['Away_Goalie'] = 'NA'

    for x in home_players:
        if x[2] == 'G':
            info_dict['Home_Goalie'] = x[0].upper()
        else:
            info_dict['Home_Goalie'] = 'NA'

    info_dict['Away_Skaters'] = len(away_players)
    info_dict['Home_Skaters'] = len(home_players)

    try:
        home_skaters = info_dict['Home_Skaters'] - 1 if info_dict['Home_Goalie'] != 'NA' else len(home_players)
        away_skaters = info_dict['Away_Skaters'] - 1 if info_dict['Away_Goalie'] != 'NA' else len(away_players)
    except KeyError:
        # Getting a key error here means that home/away goalie isn't there..which means home/away players are empty
        home_skaters = 0
        away_skaters = 0

    info_dict['Strength'] = 'x'.join([str(home_skaters), str(away_skaters)])
    # info_dict['Seconds_Elapsed']= convert_to_seconds(i[3])
    info_dict['Time_Remaining'] = event[3]
    info_dict['Ev_Zone'] = which_zone(info_dict['Description'])
    info_dict['Type'] = shot_type(event[5])

    return info_dict


def parse_html(html, players):
    """
    Parse html game pbp
    :param html: 
    :param players: players in the game (from json pbp)
    :return: 
    """

    columns = ['Period', 'Time_Remaining', 'Event', 'Description', 'Type', 'Strength', 'Ev_Zone', 'awayPlayer1',
               'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id', 'awayPlayer4',
               'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id', 'homePlayer1',
               'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3', 'homePlayer3_id', 'homePlayer4',
               'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6', 'homePlayer6_id']

    events = [parseEvent_html(event, players) for event in html if event[0] != '#']

    return pd.DataFrame(events, columns=columns)


def parseEvent_json(event, home_team, away_team):
    """
    Parses a single event when the info is in a json format
    :param event: json of event
    :param home_team: 
    :param away_team: 
    :return: dictionary with the info
    """
    play=dict()

    play['Period'] = event['about']['period']
    play['Event'] = event['result']['eventTypeId']
    play['Description'] = event['result']['description']
    play['Time_Elapsed'] = event['about']['periodTime']
    play['Seconds_Elapsed'] = convert_to_seconds(event['about']['periodTime'])
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


def parse_json(game_json, game_id):
    """
    Scrape the json for a game
    :param game_json: raw json
    :param game_id: 
    :return: DataFrame with info for the game
    """

    columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Type', 'Ev_Team'
               , 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID',  'Away_Goalie',
               'Home_Goalie', 'Away_Score', 'Home_Score', 'xC', 'yC']

    away_team = game_json['gameData']['teams']['away']['triCode']
    home_team = game_json['gameData']['teams']['home']['triCode']
    date = game_json['gameData']['datetime']['dateTime']

    plays = game_json['liveData']['plays']['allPlays'][2:]  # All the plays/events in a game

    # Go through all events and store all the info in a list
    # 'PERIOD READY' & 'PERIOD OFFICIAL' aren't found in html...so get rid of them
    events = [parseEvent_json(play, home_team, away_team) for play in plays if (play['result']['eventTypeId'] !=
                                                'PERIOD_READY' and play['result']['eventTypeId'] != 'PERIOD_OFFICIAL')]

    game_df=pd.DataFrame(events, columns=columns)

    game_df['Date'] = date[:10]
    game_df['Game_Id'] = game_id

    return game_df


def scrapeGame(game_id):
    """
    Calls getPBP and scrapes the raw PBP json and HTML
    :param game_id: game to scrape
    :return: DataFrame of game info
    """

    game_json=getPBP_json(game_id)  # Get json PBP
    game_html=getPBP_html(game_id)  # Get html PBP

    json_df = parse_json(game_json, game_id)                              # Go through json PBP
    html_df = parse_html(game_html, get_players(game_json['gameData']))   # Go through html PBP

    ##/////Fix when return false
    game_df=join_html_json_pbp(json_df, html_df)

    return game_df


def join_html_json_pbp(json_df, html_df):
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
               'homePlayer6_id', 'Away_Score', 'Home_Score', 'xC', 'yC']

    # Check if same amount of events
    if json_df.shape[0]!=html_df.shape[0]:
        return False

    # Drop from json pbp
    json = json_df.drop('Event', axis=1)
    json = json_df.drop('Away_Goalie', axis=1)
    json = json_df.drop('Home_Goalie', axis=1)

    # Drop from html pbp
    html = html_df.drop('Time_Remaining', axis=1)
    html = html_df.drop('Period', axis=1)
    html = html_df.drop('Type', axis=1)
    html = html_df.drop('Description', axis=1)

    game_df = pd.concat([html, json], axis=1)
    game_df = game_df[columns]  # Make the columns in the order specified above

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


