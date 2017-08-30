import pandas as pd
from bs4 import BeautifulSoup
import time
import shared


def event_type(play_description):
    """
    Returns the event type (ex: a SHOT or a GOAL...etc) given the event description 
    :param play_description: description of play
    :return: 
    """
    events = {'GOAL SCORED': 'GOAL', 'SHOT ON GOAL': 'SHOT', 'SHOT MISSED': 'MISS', 'SHOT BLOCKED': 'BLOCK',
              'PENALTY': 'PENL', 'FACEOFF': 'FAC', 'HIT': 'HIT', 'TAKEAWAY': 'TAKE', 'GIVEAWAY': 'GIVE'}

    event = [events[e] for e in events.keys() if e in play_description]
    return event[0] if event else None


def get_espn_game_id(date, home_team, away_team):
    """
    Scrapes the day's schedule and gets the id for the given game
    Ex: http://www.espn.com/nhl/scoreboard?date=20161024
    
    :param date: format-> YearMonthDay-> 20161024
    :param home_team: home team
    :param away_team: away team
    :return: 9 digit game id
    """
    import re

    url = 'http://www.espn.com/nhl/scoreboard?date={}'.format(date.replace('-', ''))

    response = shared.get_url(url)

    regex = re.compile(r'/nhl/recap\?gameId=(\d+)')
    game_ids = regex.findall(response.text)

    # Get teams for each game
    soup = BeautifulSoup(response.content, 'lxml')
    teams = soup.findAll('td', class_='team')
    teams = [t.get_text() for t in teams if t.get_text() != '']  # Get Rid of blanks between pair of teams
    teams = [shared.TEAMS[t.upper()] for t in teams]             # Get Tricode
    games = [teams[i:i + 2] for i in range(0, len(teams), 2)]    # Make a list of both teams for each game

    for i in range(len(games)):
        if home_team in games[i] or away_team in games[i]:
            return game_ids[i]


def get_espn(date, home_team, away_team):
    """
    Gets the ESPN pbp feed 
    Ex: http://www.espn.com/nhl/gamecast/data/masterFeed?lang=en&isAll=true&gameId=400885300
    
    :param date: date of the game
    :param home_team: home team
    :param away_team: away team
    :return: raw xml
    """
    game_id = get_espn_game_id(date, home_team.upper(), away_team.upper())
    url = 'http://www.espn.com/nhl/gamecast/data/masterFeed?lang=en&isAll=true&gameId={}'.format(game_id)

    response = shared.get_url(url)
    time.sleep(1)

    return response


def parse_event(event):
    """
    Parse each event
    In the string each field is separated by a '~'. 
    Relevant for here: The first two are the x and y coordinates. And the 4th and 5th are the time elapsed and period.
    :param event: string with info
    :return: return dict with relevant info
    """
    info = dict()
    fields = event.split('~')

    # Shootouts screw everything up so don't bother...coordinates don't matter here either way
    if fields[4] == '5':
        return None

    info['xC'] = fields[0]
    info['yC'] = fields[1]
    info['time_elapsed'] = shared.convert_to_seconds(fields[3])
    info['period'] = fields[4]
    info['event'] = event_type(fields[8].upper())

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

    columns = ['period', 'time_elapsed', 'event', 'xC', 'yC']
    plays = [parse_event(event.text) for event in events]
    plays = [play for play in plays if play is not None]

    return pd.DataFrame(plays, columns=columns)


def scrape_game(date, home_team, away_team):
    """
    Scrape the game
    :param date: ex: 2016-20-24
    :param home_team: tricode
    :param away_team: tricode
    :return: dataframe with info 
    """
    try:
        print('Using espn for pbp')
        espn_xml = get_espn(date, home_team, away_team)
    except Exception as e:
        print('Espn pbp for game {a} {b} {c} is not there'.format(a=date, b=home_team, c=away_team), e)
        return None

    try:
        espn_df = parse_espn(espn_xml)
    except Exception as e:
        print('Error for Espn pbp for game {a} {b} {c} is not there'.format(a=date, b=home_team, c=away_team), e)
        return None

    return espn_df


