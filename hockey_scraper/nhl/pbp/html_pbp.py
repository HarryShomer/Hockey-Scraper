"""
This module contains functions to scrape the Html Play by Play for any given game
"""

import re
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import hockey_scraper.utils.shared as shared


def cur_game_status(doc):
    """
    Return the game status
    
    :param doc: Html text
    
    :return: String -> one of ['Final', 'Intermission', 'Progress']
    """
    soup = BeautifulSoup(doc, "lxml")
    tables = soup.find_all('table', {'id': "GameInfo"})
    tds = tables[0].find_all('td')
    status = tds[-1].text

    # 'End' - in there means an Intermission
    # 'Final' - Game is over
    # Otherwise - It's either in progress or b4 the game started
    if 'end' in status.lower():
        return 'Intermission'
    elif 'final' in status.lower():
        return 'Final'
    else:
        return 'Live'


def get_pbp(game_id):
    """
    Given a game_id it returns the raw html
    Ex: http://www.nhl.com/scores/htmlreports/20162017/PL020475.HTM
    
    :param game_id: the game
    
    :return: raw html of game
    """
    game_id = str(game_id)
    url = 'http://www.nhl.com/scores/htmlreports/{}{}/PL{}.HTM'.format(game_id[:4], int(game_id[:4]) + 1, game_id[4:])

    page_info = {
        "url": url,
        "name": game_id,
        "type": "html_pbp",
        "season": game_id[:4],
    }

    return shared.get_file(page_info)



def get_contents(game_html):
    """
    Uses Beautiful soup to parses the html document.
    Some parsers work for some pages but don't work for others....I'm not sure why so I just try them all here in order
    
    :param game_html: html doc
    
    :return: "soupified" html 
    """
    parsers = ["html5lib", "lxml", "html.parser"]
    strainer = SoupStrainer('td', attrs={'class': re.compile(r'bborder')})

    for parser in parsers:
        # parse_only only works with lxml for some reason
        if parser == "lxml":
            soup = BeautifulSoup(game_html, parser, parse_only=strainer)
        else:
            soup = BeautifulSoup(game_html, parser)

        tds = soup.find_all("td", {"class": re.compile('.*bborder.*')})

        if len(tds) > 0:
            break

    return tds


def strip_html_pbp(td):
    """
    Strip html tags and such. (Note to Self: Don't touch this!!!) 
    
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
    soup = get_contents(html)

    # Create a list of lists (each length 8)...corresponds to 8 columns in html pbp
    td = [soup[i:i + 8] for i in range(0, len(soup), 8)]

    cleaned_html = [strip_html_pbp(x) for x in td]

    return cleaned_html


def add_home_zone(event_dict, home_team):
    """
    Determines the zone relative to the home team and add it to event.
    
    Keep in mind that the 'ev_zone' recorded is the zone relative to the event team. And for blocks the NHL counts
    the ev_team as the blocking team (I like counting the shooting team for blocks). Therefore, when it's the home team
    the zone only gets flipped when it's a block. For away teams it's the opposite.
    
    :param event_dict: dict of event info
    :param home_team: home team
    
    :return: None
    """
    ev_team = event_dict['Ev_Team']
    ev_zone = event_dict['Ev_Zone']
    event = event_dict['Event']

    # Return if we got nothing in there
    # Also just make the home zone nothing too
    if ev_zone == '':
        event_dict['Home_Zone'] = ''
        return

    # When it's either: The away team and not a block or the home team and a block
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
        event_dict['Ev_Zone'] = None
    elif zone[0].find("Off") != -1:
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
    Add event team for event. 

    Always first thing in description 
    
    :param event_dict: dict of event info
    :param event: list with parsed event info
    
    :return: None
    """
    if event_dict['Event'] in ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'PENL', 'FAC', 'HIT', 'TAKE', 'GIVE']:
        event_dict['Ev_Team'] = shared.convert_tricode(event[5].split()[0])
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
        event_dict['Seconds_Elapsed'] = 0.0


def add_score(event_dict, event, current_score, home_team):
    """
    Change if someone scored...also change current score
    
    :param event_dict: dict of parsed event stuff
    :param event: event info from pbp
    :param current_score: current score in game
    :param home_team: home team for game
    
    :return: None
    """
    event_dict['Home_Score'] = current_score['Home']
    event_dict['Away_Score'] = current_score['Away']
    event_dict['score_diff'] = current_score['Home'] - current_score['Away']

    # If it's a goal change the score
    if event[4] == 'GOAL':
        if event_dict['Ev_Team'] == home_team:
            current_score['Home'] += 1
        else:
            current_score['Away'] += 1


def get_penalty(play_description, players, home_team):
    """
    Get the penalty info
    
    :param play_description: description of play field
    :param players: all players with info
    :param home_team: home team for game
    
    :return: penalty info
    """
    # First check if it's a bench
    if "bench" in play_description or "TEAM" in play_description:
        beg_penalty_index = play_description.find("TEAM") + 5
        return play_description[beg_penalty_index: play_description.find(')') + 1]
    else:
        # If it's not a bench penl we look for the player who took the penalty
        # Get Number, and name for player who took the penalty
        num_regex = re.compile(r'#(\d+)')
        numbers = num_regex.findall(play_description)

        # If they don't have any players listed, then the description if fucked up and we got nothing
        if not numbers:
            return ''
        else:
            player = get_player_name(numbers[0], players, play_description[:3], home_team)

        # Check if the number and player match up
        if player['last_name'] is not None and player['last_name'] in play_description:
            # beg_penalty_index is right after the penalty taker's last name (+1 for whitespace)
            # Then we take from after his last name to right after the parentheses
            beg_penalty_index = play_description.find(player['last_name']) + len(player['last_name']) + 1
            return play_description[beg_penalty_index: play_description.find(')')+1]
        else:
            # This uses my old method...it falls apart for players like "Del Zotto"
            pen_regex = re.compile(r'.{3}\s+#\d+\s+\w+\s+(.*)\)')
            penalty = pen_regex.findall(play_description)
            return penalty[0] + ')' if penalty else ''


def get_player_name(number, players, team, home_team):
    """
    This function is used for the description field in the html. Given a last name and a number it return the player's 
    full name and id. Done by searching in players for the team until we find him (then just break)
    
    :param number: player's number
    :param players: all players with info
    :param team: team of player listed in html
    :param home_team: home team defined b4 hand (from json)
    
    :return: dict with full and and id
    """
    player = None
    team = shared.convert_tricode(team) # Needed to convert from new format to old
    venue = "Home" if team == home_team else "Away"

    for name in players[venue]:
        if players[venue][name]['number'] == number:
            player = {
                'name': name, 
                'id': players[venue][name]['id'], 
                'last_name': players[venue][name]['last_name']
            }
            break

    # Control for when the name can't be found
    if not player:
        player = {'name': None, 'id': None, 'last_name': None}

    return player


def if_valid_event(event):
    """
    Checks if it's a valid event ('#' is meaningless and I don't like those other one's) to parse
    
    Don't remember what 'GOFF' is but 'EGT' is for emergency goaltender. The reason I get rid of it is because it's not
    in the json and there's another 'EGPID' that can be found in both (not sure why 'EGT' exists then).
    
    Events 'PGSTR', 'PGEND', and 'ANTHEM' have been included at the start of each game for the 2017 season...I have no
    idea why. 
     
    :param event: list of stuff in pbp
    
    :return: boolean 
    """
    return event[0] != '#' and event[4] not in ['GOFF', 'EGT', 'PGSTR', 'PGEND', 'ANTHEM']


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


def parse_fac(description, players, ev_team, home_team):
    """
    Parse the description field for a face-off
    MTL won Neu. Zone - MTL #11 GOMEZ vs TOR #37 BRENT
    
    :param description: Play Description 
    :param players: players in game
    :param ev_team: Event Team
    :param home_team: Home Team for game
    
    :return: Dict with info
    """
    event_info = {}

    regex = re.compile(r'(.{3})\s+#(\d+)')
    desc = regex.findall(description)  # [[Team, num], [Team, num]]

    if ev_team == desc[0][0]:
        p1 = get_player_name(desc[0][1], players, desc[0][0], home_team)
        p2 = get_player_name(desc[1][1], players, desc[1][0], home_team)
    else:
        p1 = get_player_name(desc[1][1], players, desc[1][0], home_team)
        p2 = get_player_name(desc[0][1], players, desc[0][0], home_team)

    event_info['p1_name'] = p1['name']
    event_info['p1_ID'] = p1['id']
    event_info['p2_name'] = p2['name']
    event_info['p2_ID'] = p2['id']

    return event_info


def parse_shot_miss_take_give(description, players, ev_team, home_team):
    """
    Parse the description field for a: SHOT, MISS, TAKE, GIVE
    
    MTL ONGOAL - #81 ELLER, Wrist, Off. Zone, 11 ft.
    ANA #23 BEAUCHEMIN, Slap, Wide of Net, Off. Zone, 42 ft.
    TOR GIVEAWAY - #35 GIGUERE, Def. Zone
    TOR TAKEAWAY - #9 ARMSTRONG, Off. Zone
    
    :param description: Play Description 
    :param players: players in game
    :param ev_team: Event Team
    :param home_team: Home Team for game
    
    :return: Dict with info
    """
    event_info = {}

    regex = re.compile(r'(\d+)')
    desc = regex.search(description).groups()  # num

    p = get_player_name(desc[0], players, ev_team, home_team)
    event_info['p1_name'] = p['name']
    event_info['p1_ID'] = p['id']

    return event_info


def parse_hit(description, players, home_team):
    """
    Parse the description field for a HIT

    MTL #20 O'BYRNE HIT TOR #18 BROWN, Def. Zone

    :param description: Play Description 
    :param players: players in game
    :param home_team: Home Team for game

    :return: Dict with info
    """
    event_info = {}

    regex = re.compile(r'(.{3})\s+#(\d+)')
    desc = regex.findall(description)  # [[Team, num], [Team, num]]

    p1 = get_player_name(desc[0][1], players, desc[0][0], home_team)
    event_info['p1_name'] = p1['name']
    event_info['p1_ID'] = p1['id']

    if len(desc) > 1:
        p2 = get_player_name(desc[1][1], players, desc[1][0], home_team)
        event_info['p2_name'] = p2['name']
        event_info['p2_ID'] = p2['id']

    return event_info


def parse_block(description, players, home_team):
    """
    Parse the description field for a BLOCK
    
    MTL #76 SUBBAN BLOCKED BY TOR #2 SCHENN, Wrist, Def. Zone

    :param description: Play Description 
    :param players: players in game
    :param home_team: Home Team for game

    :return: Dict with info
    """
    event_info = {}

    regex = re.compile(r'(.{3})\s+#(\d+)')
    desc = regex.findall(description)  # [[Team, num], [Team, num]]

    if len(desc) == 0:
        event_info['p1_name'] = event_info['p2_name'] = event_info['p1_ID'] = event_info['p2_ID'] = None
    else:
        p1 = get_player_name(desc[len(desc) - 1][1], players, desc[len(desc) - 1][0], home_team)
        event_info['p1_name'] = p1['name']
        event_info['p1_ID'] = p1['id']

        if len(desc) > 1:
            p2 = get_player_name(desc[0][1], players, desc[0][0], home_team)
            event_info['p2_name'] = p2['name']
            event_info['p2_ID'] = p2['id']

    return event_info


def parse_goal(description, players, ev_team, home_team):
    """
    Parse the description field for a GOAL
    
    TOR #81 KESSEL(1), Wrist, Off. Zone, 14 ft. Assists: #42 BOZAK(1); #8 KOMISAREK(1)
    
    :param description: Play Description 
    :param players: players in game
    :param ev_team: Event Team
    :param home_team: Home Team for game

    :return: Dict with info
    """
    event_info = {}

    regex = re.compile(r'#(\d+)\s+')
    desc = regex.findall(description)  # [num, ?, ?] -> ranging from 1 to 3 indices

    p1 = get_player_name(desc[0], players, ev_team, home_team)
    event_info['p1_name'] = p1['name']
    event_info['p1_ID'] = p1['id']

    if len(desc) >= 2:
        p2 = get_player_name(desc[1], players, ev_team, home_team)
        event_info['p2_name'] = p2['name']
        event_info['p2_ID'] = p2['id']

        if len(desc) == 3:
            p3 = get_player_name(desc[2], players, ev_team, home_team)
            event_info['p3_name'] = p3['name']
            event_info['p3_ID'] = p3['id']

    return event_info


def parse_penalty(description, players, home_team):
    """
    Parse the description field for a Penalty

    MTL #81 ELLER Hooking(2 min), Def. Zone Drawn By: TOR #11 SJOSTROM

    :param description: Play Description 
    :param players: players in game
    :param home_team: Home Team for game

    :return: Dict with info
    """
    event_info = {}

    # Check if it's a Bench/Team Penalties
    if "bench" in description or "TEAM" in description:
        event_info['p1_name'] = 'Team'
    else:
        # Standard Penalty
        regex = re.compile(r'(.{3})\s+#(\d+)')
        desc = regex.findall(description)  # [[team, num], ?[team, num]] -> Either one to three indices

        if desc:
            p1 = get_player_name(desc[0][1], players, desc[0][0], home_team)
            event_info['p1_name'] = p1['name']
            event_info['p1_ID'] = p1['id']

            # When there are three the penalty was served by someone else
            # The Person who served the penalty is placed as the 3rd event player
            if len(desc) == 3:
                p3 = get_player_name(desc[1][1], players, desc[0][0], home_team)
                event_info['p3_name'] = p3['name']
                event_info['p3_ID'] = p3['id']

                p2 = get_player_name(desc[2][1], players, desc[2][0], home_team)
                event_info['p2_name'] = p2['name']
                event_info['p2_ID'] = p2['id']
            elif len(desc) == 2:
                p2 = get_player_name(desc[1][1], players, desc[1][0], home_team)
                event_info['p2_name'] = p2['name']
                event_info['p2_ID'] = p2['id']

    return event_info


def add_event_players(event_dict, event, players, home_team):
    """
    Add players involved in the event to event_dict
    
    :param event_dict: dict of parsed event stuff
    :param event: fixed up html
    :param players: dict of players and id's
    :param home_team: home team
    
    :return: None
    """
    event_info = {}
    description = event[5].strip()
    ev_team = shared.convert_tricode(description.split()[0])

    if event[4] == 'FAC':
        event_info = parse_fac(description, players, ev_team, home_team)
    elif event[4] in ['SHOT', 'MISS', 'GIVE', 'TAKE']:
        event_info = parse_shot_miss_take_give(description, players, ev_team, home_team)
    elif event[4] == 'HIT':
        event_info = parse_hit(description, players, home_team)
    elif event[4] == 'BLOCK':
        event_info = parse_block(description, players, home_team)
    elif event[4] == 'GOAL':
        event_info = parse_goal(description, players, ev_team, home_team)
    elif event[4] == 'PENL':
        event_info = parse_penalty(description, players, home_team)

    # Transfer info over
    for key in event_info:
        event_dict[key] = event_info[key]


def populate_players(event_dict, players, away_players, home_players):
    """
    Populate away and home player info (and num skaters on each side).

    These include:
        1. HomePlayer & AwayPlayers fields from 1-6 for name/id
        2. Home & Away Goalie Fields for name/id
    
    :param event_dict: dict with event info
    :param players: all players in game and info
    :param away_players: players for away team
    :param home_players: players for home team
    
    :return: None
    """
    for venue in ['Home', 'Away']:
        for j in range(6):
            # Deal with the Home & Away Player Fields
            try:
                ven_player = home_players[j] if venue == "Home" else away_players[j]
                name = shared.fix_name(ven_player[0])
                event_dict['{}Player{}'.format(venue.lower(), j + 1)] = name
                event_dict['{}Player{}_id'.format(venue.lower(), j + 1)] = players[venue][name]['id']
            except KeyError:
                event_dict['{}Player{}_id'.format(venue.lower(), j + 1)] = None
            except IndexError:
                event_dict['{}Player{}'.format(venue.lower(), j + 1)] = None
                event_dict['{}Player{}_id'.format(venue.lower(), j + 1)] = None
                continue

            # If the player is a goalie we try filling that field
            if ven_player[2] == "G":
                try:
                    event_dict['{}_Goalie'.format(venue)] = name
                    event_dict['{}_Goalie_Id'.format(venue)] = players[venue][name]['id']
                except KeyError:
                    pass

        # Control for when no goalies present
        if '{}_Goalie'.format(venue) not in event_dict:
            event_dict['{}_Goalie'.format(venue)] = None
        if '{}_Goalie_Id'.format(venue) not in event_dict:
            event_dict['{}_Goalie_Id'.format(venue)] = None


    event_dict['Away_Players'] = len(away_players)
    event_dict['Home_Players'] = len(home_players)


def parse_event(event, players, home_team, current_score):
    """
    Receives an event and parses it
    
    :param event: event type
    :param players: players in game
    :param home_team: home team
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

    # Sometimes it's empty...(they seem to sometimes/always have a whitespace char)
    if len(event_dict['Description']) > 1:
        add_event_players(event_dict, event, players, home_team)

    return event_dict


def parse_html(html, players, teams):
    """
    Parse html game pbp
    
    :param html: raw html
    :param players: players in the game (from json pbp)
    :param teams: dict with home and away teams
    
    :return: DataFrame with info
    """
    columns = ['Period', 'Event', 'Description', 'Time_Elapsed', 'Seconds_Elapsed', 'Strength', 'Ev_Zone', 'Type',
               'Ev_Team', 'Home_Zone', 'Away_Team', 'Home_Team', 'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name',
               'p3_ID', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id',
               'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id',
               'homePlayer1', 'homePlayer1_id', 'homePlayer2', 'homePlayer2_id', 'homePlayer3', 'homePlayer3_id',
               'homePlayer4', 'homePlayer4_id', 'homePlayer5', 'homePlayer5_id', 'homePlayer6', 'homePlayer6_id',
               'Away_Goalie', 'Away_Goalie_Id', 'Home_Goalie', 'Home_Goalie_Id', 'Away_Players', 'Home_Players',
               'Away_Score', 'Home_Score']

    current_score = {'Home': 0, 'Away': 0}
    events = [parse_event(event, players, teams['Home'], current_score) for event in html if if_valid_event(event)]

    df = pd.DataFrame(list(events), columns=columns)

    # This is seen sometimes...it's a duplicate row
    df.drop(df[df.Time_Elapsed == '-16:0-'].index, inplace=True)

    df['p1_ID'] = df['p1_ID'].astype("float64")
    df['Away_Team'] = teams['Away']
    df['Home_Team'] = teams['Home']

    return df


def scrape_pbp(game_html, game_id, players, teams):
    """
    Scrape the data for the pbp

    :param game_html: Html doc for the game
    :param game_id: game to scrape
    :param players: dict with player info
    :param teams: dict with home and away teams

    :return: DataFrame of game info or None if it fails
    """
    if not game_html:
        shared.print_error("Html pbp for game {} is either not there or can't be obtained".format(game_id))
        return None

    cleaned_html = clean_html_pbp(game_html)

    if len(cleaned_html) == 0:
        shared.print_error("Html pbp contains no plays, this game can't be scraped")
        return None

    try:
        game_df = parse_html(cleaned_html, players, teams)
    except Exception as e:
        shared.print_error('Error parsing Html pbp for game {} {}'.format(game_id, e))
        return None

    # These sometimes end up as objects
    game_df.Period = game_df.Period.astype(int)
    game_df.Seconds_Elapsed = game_df.Seconds_Elapsed.astype(float)

    return game_df


def scrape_game_live(game_id, players, teams):
    """
    Scrape the data for the game when it's live
    
    :param game_id: game to scrape
    :param players: dict with player info
    :param teams: dict with home and away teams
    
    :return: Tuple - get_pbp(), cur_game_status()
    """
    game_html = get_pbp(game_id)
    return scrape_pbp(game_html, game_id, players, teams), cur_game_status(game_html)


def scrape_game(game_id, players, teams):
    """ 
    Scrape the data for the game when not live
    
    :param game_id: game to scrape
    :param players: dict with player info
    :param teams: dict with home and away teams
    
    :return: DataFrame of game info or None if it fails
    """
    game_html = get_pbp(game_id)
    return scrape_pbp(game_html, game_id, players, teams)


