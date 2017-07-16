import pandas as pd
import requests
import json
import time
import shared_functions


def get_pbp(game_id):
    """
    Given a game_id it returns the raw json
    :param game_id: the game
    :return: raw json of game
    """
    url = 'http://statsapi.web.nhl.com/api/v1/game/{}/feed/live'.format(game_id)

    response = requests.get(url)
    response.raise_for_status()

    pbp_json = json.loads(response.text)
    time.sleep(1)

    return pbp_json


def get_teams(json):
    """
    Get teams 
    :param json: pbp json
    :return: dict with home adn away
    """
    return {'Home': shared_functions.TEAMS[json['gameData']['teams']['home']['name'].upper()],
            'Away': shared_functions.TEAMS[json['gameData']['teams']['away']['name'].upper()]}


def parse_event(event, home_team, away_team):
    """
    Parses a single event when the info is in a json format
    :param event: json of event
    :param home_team: 
    :param away_team: 
    :return: dictionary with the info
    """
    play = dict()

    play['Period'] = event['about']['period']
    play['Event'] = event['result']['eventTypeId']
    play['Description'] = event['result']['description']
    play['Time_Elapsed'] = event['about']['periodTime']
    play['Seconds_Elapsed'] = shared_functions.convert_to_seconds(event['about']['periodTime'])
    play['Away_Team'] = away_team
    play['Home_Team'] = home_team

    # If there's a players key that means an event occurred on the play.
    if 'players' in event.keys():
        play['Ev_Team'] = shared_functions.TEAMS[event['team']['name'].upper()]

        # NHL has Ev_Team for blocked shot as team who blocked it...flip it
        if play['Event'] == 'BLOCKED_SHOT':
            play['Ev_Team'] = away_team if play['Ev_Team'] == home_team else home_team

        play['p1_name'] = event['players'][0]['player']['fullName']
        play['p1_ID'] = event['players'][0]['player']['id']

        for i in range(len(event['players'])):
            if event['players'][i]['playerType'] != 'Goalie':
                play['p{}_name'.format(i + 1)] = event['players'][i]['player']['fullName'].upper()
                play['p{}_ID'.format(i + 1)] = event['players'][i]['player']['id']

        """
        # If it's a penalty include the type->minor/double/major...etc
        if play['Event'] == 'PENALTY':
            play['Type'] = '-'.join([event['result']['secondaryType'], event['result']['penaltySeverity']])
        else:
            try:
                play['Type'] = event['result'][
                    'secondaryType'].upper()  # Events like Faceoffs don't have secondaryType's
            except KeyError:
                play['Type'] = ''
        """

        # Coordinates aren't always there
        try:
            play['xC'] = event['coordinates']['x']
            play['yC'] = event['coordinates']['y']
        except KeyError:
            play['xC'] = 'Na'
            play['yC'] = 'Na'

    # Sometimes they record events for shots in the wrong zone (or maybe not)...so change it
    if play['Event'] == 'MISS' or play['Event'] == 'SHOT' or play['Event'] == 'GOAL' or play['Event'] == 'BLOCK':

        if play['Ev_Team'] == home_team:
            # X should be negative in 1st and 3rd for home_team
            if (play['Period'] == 1 or play['Period'] == 3) and play['xC'] > 0:
                play['xC'] = -int(play['xC'])
                play['yC'] = -int(play['yC'])
            elif play['Period'] == 2 and play['xC'] < 0:
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
    :return: Either a DataFrame with info for the game 
    """

    columns = ['Game_Id', 'Date', 'Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Ev_Team'
        , 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID', 'xC', 'yC']

    away_team = game_json['gameData']['teams']['away']['abbreviation']  # TriCode
    home_team = game_json['gameData']['teams']['home']['abbreviation']  # TriCode
    date = game_json['gameData']['datetime']['dateTime']
    plays = game_json['liveData']['plays']['allPlays'][2:]  # All the plays/events in a game

    # Go through all events and store all the info in a list
    # 'PERIOD READY' & 'PERIOD OFFICIAL' aren't found in html...so get rid of them
    events = [parse_event(play, home_team, away_team) for play in plays if (play['result']['eventTypeId'] !=
                                                                            'PERIOD_READY' and play['result'][
                                                                            'eventTypeId'] != 'PERIOD_OFFICIAL')]
    game_df = pd.DataFrame(events, columns=columns)

    # Sometimes the dateTime does the next day so just take the date stamped for the first play
    game_df['Date'] = game_json['liveData']['plays']['allPlays'][0]['about']['dateTime'][:10]
    game_df['Game_Id'] = game_id

    return game_df


def scrapeGame(game_id):
    """
    Used for debugging 
    :param game_id: game to scrape
    :return: DataFrame of game info
    """
    try:
        game_json = get_pbp(game_id)
    except requests.exceptions.HTTPError as e:
        print('Json pbp for game {} is not there'.format(game_id), e)
        return None

    try:
        game_df = parse_json(game_json, game_id)
    except Exception as e:
        print('Error for Json pbp for game {}'.format(game_id), e)
        return None

    return game_df

