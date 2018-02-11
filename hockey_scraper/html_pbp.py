"""
This module contains functions to scrape the Html Play by Play for any given game
"""

import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import re
import hockey_scraper.shared as shared


def get_pbp(game_id):
    """
    Given a game_id it returns the raw html
    Ex: http://www.nhl.com/scores/htmlreports/20162017/PL020475.HTM
    
    :param game_id: the game
    
    :return: raw html of game
    """
    game_id = str(game_id)
    url = 'http://www.nhl.com/scores/htmlreports/{}{}/PL{}.HTM'.format(game_id[:4], int(game_id[:4]) + 1, game_id[4:])

    return shared.get_url(url)


def get_soup(game_html):
    """
    Uses Beautiful soup to parses the html document.
    Some parsers work for some pages but don't work for others....I'm not sure why so I just try them all here in order
    
    :param game_html: html doc
    
    :return: "soupified" html and player_shifts portion of html (it's a bunch of td tags)
    """
    strainer = SoupStrainer('td', attrs={'class': re.compile(r'bborder')})
    soup = BeautifulSoup(game_html.text, "lxml", parse_only=strainer)
    soup = soup.select('td.+.bborder')

    if len(soup) == 0:
        soup = BeautifulSoup(game_html.text, "html.parser", parse_only=strainer)
        soup = soup.select('td.+.bborder')

        if len(soup) == 0:
            soup = BeautifulSoup(game_html.text, "html5lib")
            soup = soup.select('td.+.bborder')

    return soup


def strip_html_pbp(td):
    """
    Strip html tags and such 
    
    :param td: pbp
    
    :return: list of plays (which contain a list of info) stripped of html
    """

    for y in range(len(td)):
        # Get the 'br' tag for the time column...this get's us time remaining instead of elapsed and remaining combined
        if y == 3:
            td[y] = td[y].get_text()   # This gets us elapsed and remaining combined-< 3:0017:00
            index = td[y].find(':')
            td[y] = td[y][:index+3]
        elif (y == 6 or y == 7) and td[0] != '#':
            # 6 & 7-> These are the player 1 ice one's
            # The second statement controls for when it's just a header
            baz = td[y].find_all('td')
            bar = [baz[z] for z in range(len(baz)) if z % 4 != 0]  # Because of previous step we get repeats...delete some

            # The setup in the list is now: Name/Number->Position->Blank...and repeat
            # Now strip all the html
            players = []
            for i in range(len(bar)):
                if i % 3 == 0:
                    try:
                        name = return_name_html(bar[i].find('font')['title'])
                        number = bar[i].get_text().strip('\n')  # Get number and strip leading/trailing newlines
                    except KeyError:
                        name = ''
                        number = ''
                elif i % 3 == 1:
                    if name != '':
                        position = bar[i].get_text()
                        players.append([name, number, position])

            td[y] = players
        else:
            td[y] = td[y].get_text()

    return td


def clean_html_pbp(html):
    """
    Get rid of html and format the data
    
    :param html: the requested url
    
    :return: a list with all the info
    """
    soup = get_soup(html)

    # Create a list of lists (each length 8)...corresponds to 8 columns in html pbp
    td = [soup[i:i + 8] for i in range(0, len(soup), 8)]

    cleaned_html = [strip_html_pbp(x) for x in td]

    return cleaned_html


def add_home_zone(event_dict, home_team):
    """
    Determines the zone relative to the home team and add it to event
    
    :param event_dict: dict of event info
    :param home_team: home team
    
    :return: None
    """
    ev_team = event_dict['Ev_Team']
    ev_zone = event_dict['Ev_Zone']
    event = event_dict['Event']

    if ev_zone == '':
        event_dict['Home_Zone'] = ''
        return

    if (ev_team != home_team and event != 'BLOCK') or (ev_team == home_team and event == 'BLOCK'):
        if ev_zone == 'Off':
            event_dict['Home_Zone'] = 'Def'
        elif ev_zone == 'Def':
            event_dict['Home_Zone'] = 'Off'
        else:
            event_dict['Home_Zone'] = ev_zone
    else:
        event_dict['Home_Zone'] = ev_zone


def add_zone(event_dict, play_description):
    """
    Determine which zone the play occurred in (unless one isn't listed) and add it to dict
    
    :param event_dict: dict of event info
    :param play_description: the zone would be included here
    
    :return: Off, Def, Neu, or NA
    """
    s = [x.strip() for x in play_description.split(',')]  # Split by comma's into a list
    zone = [x for x in s if 'Zone' in x]  # Find if list contains which zone

    if not zone:
        event_dict['Ev_Zone'] = ''
        return

    if zone[0].find("Off") != -1:
        event_dict['Ev_Zone'] = 'Off'
    elif zone[0].find("Neu") != -1:
        event_dict['Ev_Zone'] = 'Neu'
    elif zone[0].find("Def") != -1:
        event_dict['Ev_Zone'] = 'Def'


def add_type(event_dict, event, players, home_team):
    """
    Add "type" for event -> either a penalty or a shot type
    
    :param event_dict: dict of event info
    :param event: list with parsed event info
    :param players: dict of home and away players in game
    :param home_team: home team for game
    
    :return: None
    """
    if 'PENL' in event[4]:
        event_dict['Type'] = get_penalty(event[5], players, home_team)
    else:
        event_dict['Type'] = shot_type(event[5]).upper()


def add_strength(event_dict, home_players, away_players):
    """
    Get strength for event -> It's home then away
    
    :param event_dict: dict of event info
    :param home_players: list of players for home team
    :param away_players: list of players for away team
    
    :return: None
    """
    try:
        home_skaters = event_dict['Home_Players'] - 1 if event_dict['Home_Goalie'] != '' else len(home_players)
        away_skaters = event_dict['Away_Players'] - 1 if event_dict['Away_Goalie'] != '' else len(away_players)
    except KeyError:
        # Getting a key error here means that home/away goalie isn't there...which means home/away players are empty
        home_skaters = 0
        away_skaters = 0

    event_dict['Strength'] = 'x'.join([str(home_skaters), str(away_skaters)])


def add_event_team(event_dict, event):
    """
    Add event team for event 
    
    :param event_dict: dict of event info
    :param event: list with parsed event info
    
    :return: None
    """
    if event_dict['Event'] in ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'PENL', 'FAC', 'HIT', 'TAKE', 'GIVE']:
        # Split the description and take the first thing (which is the team)
        event_dict['Ev_Team'] = event[5].split()[0]
    else:
        event_dict['Ev_Team'] = ''


def add_period(event_dict, event):
    """
    Add period for event 
    
    :param event_dict: dict of event info
    :param event: list with parsed event info
    
    :return: None
    """
    try:
        event_dict['Period'] = int(event[1])
    except ValueError:
        event_dict['Period'] = 0


def add_time(event_dict, event):
    """
    Fill in time and seconds elapsed
    
    :param event_dict: dict of parsed event stuff
    :param event: event info from pbp
    
    :return: None
    """
    event_dict['Time_Elapsed'] = str(event[3])

    if event[3] != '':
        event_dict['Seconds_Elapsed'] = shared.convert_to_seconds(event[3])
    else:
        event_dict['Seconds_Elapsed'] = ''


def add_score(event_dict, event, current_score, home_team):
    """
    Change if someone scored...also change current score
    
    :param event_dict: dict of parsed event stuff
    :param event: event info from pbp
    :param current_score: current score in game
    :param home_team: home team for game
    
    :return: None
    """

    # If it's a goal change the score
    if event[4] == 'GOAL':
        if event_dict['Ev_Team'] == home_team:
            current_score['Home'] += 1
        else:
            current_score['Away'] += 1

    event_dict['Home_Score'] = current_score['Home']
    event_dict['Away_Score'] = current_score['Away']
    event_dict['score_diff'] = current_score['Home'] - current_score['Away']


# TODO: Fix penalty name -> fucks up with names like Del Zotto
# Note: Remember master list player name != html name!!!!!!!!
def get_penalty(play_description, players, home_team):
    """
    Get the penalty info
    
    :param play_description: description of play field
    :param players: all players with info
    :param home_team: home team for game
    
    :return: penalty info
     # Get player who took the penalty
    player_regex = re.compile(r'(.{3})\s+#(\d+)')
    desc = player_regex.findall(play_description)
    player = get_player_name(desc[0][1], players, desc[0][0], home_team)

    # Find where in the description his name is located
    player_index = play_description.find(player)
    if player_index == -1:
        return
        
    player_description[player_index+len(players): play_description.find(")"]
    """
    regex = re.compile(r'.{3}\s+#\d+\s+\w+\s+(.*)\)')
    penalty = regex.findall(play_description)

    if penalty:
        return penalty[0] + ')'
    else:
        return ''


def get_player_name(number, players, team, home_team):
    """
    This function is used for the description field in the html. Given a last name and a number it return the player's 
    full name and id.
    
    :param number: player's number
    :param players: all players with info
    :param team: team of player
    :param home_team: home team
    
    :return: dict with full and and id
    """

    if team == home_team:
        player = [{'name': name, 'id': players['Home'][name]['id']} for name in players['Home'].keys() if
                  players['Home'][name]['number'] == number]
    else:
        player = [{'name': name, 'id': players['Away'][name]['id']} for name in players['Away'].keys() if
                  players['Away'][name]['number'] == number]

    if not player:
        player = [{'name': '', 'id': ''}]  # Control for when the name can't be found

    return player[0]


def if_valid_event(event):
    """
    Checks if it's a valid event ('#' is meaningless and I don't like the other ones) to parse
    
    :param event: list of stuff in pbp
    
    :return: boolean 
    """
    if event[4] != 'GOFF' and event[0] != '#' and event[4] != 'CHL':
        return True
    else:
        return False


def return_name_html(info):
    """
    In the PBP html the name is in a format like: 'Center - MIKE RICHARDS'
    Some also have a hyphen in their last name so can't just split by '-'
    
    :param info: position and name
    
    :return: name
    """
    s = info.index('-')  # Find first hyphen
    return info[s + 1:].strip(' ')  # The name should be after the first hyphen


def shot_type(play_description):
    """
    Determine which zone the play occurred in (unless one isn't listed)
    
    :param play_description: the type would be in here
    
    :return: the type if it's there (otherwise just NA)
    """
    types = ['wrist', 'snap', 'slap', 'deflected', 'tip-in', 'backhand', 'wrap-around']

    play_description = [x.strip() for x in play_description.split(',')]  # Strip leading and trailing whitespace
    play_description = [i.lower() for i in play_description]  # Convert to lowercase

    for p in play_description:
        if p in types:
            if p == 'wrist' or p == 'slap' or p == 'snap':
                return ' '.join([p, 'shot'])
            else:
                return p
    return ''


def add_event_players(event_dict, event, players, home_team):
    """
    Add players involved in the event to event_dict
    
    :param event_dict: dict of parsed event stuff
    :param event: fixed up html
    :param players: dict of players and id's
    :param home_team: home team
    
    :return: None
    """
    description = event[5].strip()
    ev_team = description.split()[0]

    if event[4] == 'FAC':
        # MTL won Neu. Zone - MTL #11 GOMEZ vs TOR #37 BRENT
        regex = re.compile(r'(.{3})\s+#(\d+)')
        desc = regex.findall(description)  # [[Team, num], [Team, num]]

        if ev_team == desc[0][0]:
            p1 = get_player_name(desc[0][1], players, desc[0][0], home_team)
            p2 = get_player_name(desc[1][1], players, desc[1][0], home_team)
        else:
            p1 = get_player_name(desc[1][1], players, desc[1][0], home_team)
            p2 = get_player_name(desc[0][1], players, desc[0][0], home_team)

        event_dict['p1_name'] = p1['name']
        event_dict['p1_ID'] = p1['id']
        event_dict['p2_name'] = p2['name']
        event_dict['p2_ID'] = p2['id']

    elif event[4] in ['SHOT', 'MISS', 'GIVE', 'TAKE']:
        # MTL ONGOAL - #81 ELLER, Wrist, Off. Zone, 11 ft.
        # ANA #23 BEAUCHEMIN, Slap, Wide of Net, Off. Zone, 42 ft.
        # TOR GIVEAWAY - #35 GIGUERE, Def. Zone
        # TOR TAKEAWAY - #9 ARMSTRONG, Off. Zone
        regex = re.compile(r'(\d+)')
        desc = regex.search(description).groups()  # num

        p = get_player_name(desc[0], players, ev_team, home_team)
        event_dict['p1_name'] = p['name']
        event_dict['p1_ID'] = p['id']

    elif event[4] == 'HIT':
        # MTL #20 O'BYRNE HIT TOR #18 BROWN, Def. Zone
        regex = re.compile(r'(.{3})\s+#(\d+)')
        desc = regex.findall(description)  # [[Team, num], [Team, num]]

        p1 = get_player_name(desc[0][1], players, desc[0][0], home_team)
        event_dict['p1_name'] = p1['name']
        event_dict['p1_ID'] = p1['id']

        if len(desc) > 1:
            p2 = get_player_name(desc[1][1], players, desc[1][0], home_team)
            event_dict['p2_name'] = p2['name']
            event_dict['p2_ID'] = p2['id']

    elif event[4] == 'BLOCK':
        # MTL #76 SUBBAN BLOCKED BY TOR #2 SCHENN, Wrist, Def. Zone
        regex = re.compile(r'(.{3})\s+#(\d+)')
        desc = regex.findall(description)  # [[Team, num], [Team, num]]

        p1 = get_player_name(desc[len(desc)-1][1], players, desc[len(desc)-1][0], home_team)
        event_dict['p1_name'] = p1['name']
        event_dict['p1_ID'] = p1['id']

        if len(desc) > 1:
            p2 = get_player_name(desc[0][1], players, desc[0][0], home_team)
            event_dict['p2_name'] = p2['name']
            event_dict['p2_ID'] = p2['id']

    elif event[4] == 'GOAL':
        # TOR #81 KESSEL(1), Wrist, Off. Zone, 14 ft. Assists: #42 BOZAK(1); #8 KOMISAREK(1)
        regex = re.compile(r'#(\d+)\s+')
        desc = regex.findall(description)  # [num, ?, ?] -> ranging from 1 to 3 indices

        p1 = get_player_name(desc[0], players, ev_team, home_team)
        event_dict['p1_name'] = p1['name']
        event_dict['p1_ID'] = p1['id']

        if len(desc) >= 2:
            p2 = get_player_name(desc[1], players, ev_team, home_team)
            event_dict['p2_name'] = p2['name']
            event_dict['p2_ID'] = p2['id']

            if len(desc) == 3:
                p3 = get_player_name(desc[2], players, ev_team, home_team)
                event_dict['p3_name'] = p3['name']
                event_dict['p3_ID'] = p3['id']

    elif event[4] == 'PENL':
        # MTL #81 ELLER Hooking(2 min), Def. Zone Drawn By: TOR #11 SJOSTROM

        # Check if it's a team penalty
        if 'Served' in description or 'TEAM' in description:
            event_dict['p1_name'] = 'Team'
        else:
            regex = re.compile(r'(.{3})\s+#(\d+)')
            desc = regex.findall(description)  # [[team, num], ?[team, num]] -> Either one or two indices

            if desc:
                p1 = get_player_name(desc[0][1], players, desc[0][0], home_team)
                event_dict['p1_name'] = p1['name']
                event_dict['p1_ID'] = p1['id']

            if len(desc) == 2:
                p2 = get_player_name(desc[1][1], players, desc[1][0], home_team)
                event_dict['p2_name'] = p2['name']
                event_dict['p2_ID'] = p2['id']


def populate_players(event_dict, players, away_players, home_players):
    """
    Populate away and home player info (and num skaters on each side)
    NOTE: Could probably do this in a much neater way...
    
    :param event_dict: dict with event info
    :param players: all players in game and info
    :param away_players: players for away team
    :param home_players: players for home team
    
    :return: None
    """
    for j in range(6):
        try:
            name = shared.fix_name(away_players[j][0].upper())
            event_dict['awayPlayer{}'.format(j + 1)] = name
            event_dict['awayPlayer{}_id'.format(j + 1)] = players['Away'][name]['id']
        except KeyError:
            event_dict['awayPlayer{}_id'.format(j + 1)] = 'NA'
        except IndexError:
            event_dict['awayPlayer{}'.format(j + 1)] = ''
            event_dict['awayPlayer{}_id'.format(j + 1)] = ''

        try:
            name = shared.fix_name(home_players[j][0].upper())
            event_dict['homePlayer{}'.format(j + 1)] = name
            event_dict['homePlayer{}_id'.format(j + 1)] = players['Home'][name]['id']
        except KeyError:
            event_dict['homePlayer{}_id'.format(j + 1)] = 'NA'
        except IndexError:
            event_dict['homePlayer{}'.format(j + 1)] = ''
            event_dict['homePlayer{}_id'.format(j + 1)] = ''

    # Did this because above method assumes the goalie is at end of player list
    for x in away_players:
        if x[2] == 'G':
            event_dict['Away_Goalie'] = shared.fix_name(x[0].upper())
            try:
                event_dict['Away_Goalie_Id'] = players['Away'][event_dict['Away_Goalie']]['id']
            except KeyError:
                event_dict['Away_Goalie_Id'] = 'NA'
        else:
            event_dict['Away_Goalie'] = ''
            event_dict['Away_Goalie_Id'] = ''

    for x in home_players:
        if x[2] == 'G':
            event_dict['Home_Goalie'] = shared.fix_name(x[0].upper())
            try:
                event_dict['Home_Goalie_Id'] = players['Home'][event_dict['Home_Goalie']]['id']
            except KeyError:
                event_dict['Home_Goalie_Id'] = 'NA'
        else:
            event_dict['Home_Goalie'] = ''
            event_dict['Home_Goalie_Id'] = ''

    event_dict['Away_Players'] = len(away_players)
    event_dict['Home_Players'] = len(home_players)


def parse_event(event, players, home_team, if_plays_in_json, current_score):
    """
    Receives an event and parses it
    
    :param event: event type
    :param players: players in game
    :param home_team: home team
    :param if_plays_in_json: If the pbp json contains the plays
    :param current_score: current score for both teams
    
    :return: dict with info
    """
    event_dict = dict()

    away_players = event[6]
    home_players = event[7]

    event_dict['Description'] = event[5]
    event_dict['Event'] = str(event[4])

    add_period(event_dict, event)
    add_time(event_dict, event)
    add_event_team(event_dict, event)
    add_score(event_dict, event, current_score, home_team)
    populate_players(event_dict, players, away_players, home_players)
    add_strength(event_dict, home_players, away_players)
    add_type(event_dict, event, players, home_team)
    add_zone(event_dict, event[5])
    add_home_zone(event_dict, home_team)

    # I like getting the event players from the json
    if not if_plays_in_json:
        if event_dict['Event'] in ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'PENL', 'FAC', 'HIT', 'TAKE', 'GIVE']:
            add_event_players(event_dict, event, players, home_team)

    return event_dict


def parse_html(html, players, teams, if_plays_in_json):
    """
    Parse html game pbp
    
    :param html: raw html
    :param players: players in the game (from json pbp)
    :param teams: dict with home and away teams
    :param if_plays_in_json: If the pbp json contains the plays
    
    :return: DataFrame with info
    """
    if if_plays_in_json:
        columns = ['Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength', 'Ev_Zone', 'Type',
                   'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2',
                   'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5',
                   'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2',
                   'homePlayer2_id', 'homePlayer3', 'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5',
                   'homePlayer5_id', 'homePlayer6', 'homePlayer6_id', 'Away_Goalie', 'Away_Goalie_Id', 'Home_Goalie',
                   'Home_Goalie_Id', 'Away_Players', 'Home_Players', 'Away_Score', 'Home_Score']
    else:
        columns = ['Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength', 'Ev_Zone', 'Type',
                   'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name',
                   'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id',
                   'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id',
                   'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3', 'homePlayer3_id',
                   'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6', 'homePlayer6_id',
                   'Away_Goalie', 'Away_Goalie_Id', 'Home_Goalie', 'Home_Goalie_Id', 'Away_Players', 'Home_Players',
                   'Away_Score', 'Home_Score']

    current_score = {'Home': 0, 'Away': 0}
    events = [parse_event(event, players, teams['Home'], if_plays_in_json, current_score)
              for event in html if if_valid_event(event)]

    df = pd.DataFrame(list(events), columns=columns)

    df.drop(df[df.Time_Elapsed == '-16:0-'].index, inplace=True)       # This is seen sometimes...it's a duplicate row

    df['Away_Team'] = teams['Away']
    df['Home_Team'] = teams['Home']

    return df


def scrape_game(game_id, players, teams, if_plays_in_json):
    """ 
    Scrape the data for the game
    
    :param game_id: game to scrape
    :param players: dict with player info
    :param teams: dict with home and away teams
    :param if_plays_in_json: boolean, if the plays are in the json
    
    :return: DataFrame of game info or None if it fails
    """
    game_html = get_pbp(game_id)

    if not game_html:
        print("Html pbp for game {} is either not there or can't be obtained".format(game_id))
        return None

    cleaned_html = clean_html_pbp(game_html)

    if len(cleaned_html) == 0:
        print("Html pbp contains no plays, this game can't be scraped")
        return None

    try:
        game_df = parse_html(cleaned_html, players, teams, if_plays_in_json)
    except Exception as e:
        print('Error parsing Html pbp for game {}'.format(game_id), e)
        return None

    return game_df


