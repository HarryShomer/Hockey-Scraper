import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import shared_functions


def get_espn_game_id(date, home_team, away_team):
    """
    Scrapes the day's schedule and gets the id for the given game
    :param date: format-> YearMonthDay-> 20161024
    :param home_team: 
    :param away_team: 
    :return: 9 digit game id
    """
    url = 'http://www.espn.com/nhl/scoreboard?date={}'.format(date.replace('-', ''))
    response = requests.get(url)
    response.raise_for_status()
    time.sleep(1)

    text = response.text

    index = 0
    game_ids = []

    # Find all game id's
    while index < len(response.text):
        index = response.text.find('/nhl/recap?gameId=', index)
        if index == -1:
            break
        game_ids.append(text[index + 18:index + 27])  # Move to end of substring and get game id
        index += 2

    # Get teams for each game
    soup = BeautifulSoup(response.content, 'html.parser')
    teams = soup.findAll('td', class_='team')
    teams = [t.get_text() for t in teams if t.get_text() != '']  # Get Rid of blanks between pair of teams
    teams = [shared_functions.TEAMS[t.upper()] for t in teams]  # Get Tricode
    games = [teams[i:i + 2] for i in range(0, len(teams), 2)]  # Make a list of both teams for each game

    for i in range(len(games)):
        if home_team in games[i] or away_team in games[i]:
            return game_ids[i]


def get_espn(date, home_team, away_team):
    """
    Gets the ESPN pbp feed 
    :param date: date of the game
    :param home_team: 
    :param away_team: 
    :return: raw xml
    """
    game_id = get_espn_game_id(date, shared_functions.TEAMS[home_team.upper()], shared_functions.TEAMS[away_team.upper()])
    url = 'http://www.espn.com/nhl/gamecast/data/masterFeed?lang=en&isAll=true&gameId={}'.format(game_id)

    response = requests.get(url)
    response.raise_for_status()
    time.sleep(1)

    return parse_espn(response)


def parse_event_espn(event):
    """
    Parse each event
    In the string each field is separated by a '~'. 
    Relevant for here: The first two are the x and y coordinates. And the 4th and 5th are the time elapsed and period.
    :param event: string with info
    :return: return dict with relevant info
    """
    info = dict()
    fields = event.split('~')

    info['xC'] = fields[0]
    info['yC'] = fields[1]
    #info['Time_Remaining'] = shared_functions.convert_to_seconds(fields[3])
    #info['Period'] = fields[4]

    return info


def parse_espn(espn_xml):
    """
    Parse feed 
    :param espn_xml: raw xml of feed
    :return: DataFrame with info
    """
    import xml.etree.ElementTree as etree
    tree = etree.fromstring(espn_xml.text)
    events = tree[1]

    # columns = ['Period', 'Time_Remaining', 'xC', 'yC']
    columns = ['xC', 'yC']

    plays = [parse_event_espn(event.text) for event in events]
    df = pd.DataFrame(plays, columns=columns)

    # Sort by period by time...the plays aren't always in order
    df = df.sort_values(by=['Period', 'Time_Remaining'], ascending=[True, True])

    return df

