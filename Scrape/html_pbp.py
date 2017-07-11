import pandas as pd
from bs4 import BeautifulSoup
import requests
import shared_functions


def getPBP_html(game_id):
    """
    Given a game_id it returns the raw html
    :param game_id: the game
    :return: raw html of game
    """
    game_id = str(game_id)
    url = 'http://www.nhl.com/scores/htmlreports/{}{}/PL{}.HTM'.format(game_id[:4], int(game_id[:4]) + 1, game_id[4:])

    response = requests.get(url)
    response.raise_for_status()

    return response


def get_penalty(play_description):
    """
    Get the penalty info
    :param play_description: 
    :return: penalty info
    MTL #81 ELLER Hooking(2 min), Def. Zone Drawn By: TOR #11 SJOSTROM
    T.B #88 VASILEVSKIY Delaying Game-Puck over glass(2 min) Served By: #27 DROUIN, Def. Zone
    """
    play_description = play_description.split()

    for i in range(len(play_description)):
        if ')' in play_description[i]:  # Search for end of time for penalty
            penalty = ' '.join(
                [play_description[j] for j in range(3, i + 1)])  # Join from after player name until index
            return penalty.strip(',')

    return 'NA'


def get_player_name(last_name, number, players, team, home_team):
    """
    This function is used for the description field in the html
    Given a last name and a number return the player's full name

     

    :param last_name: 
    :param number: 
    :param players: all players with info
    :param team: team of player
    :param home_team
    :return: 
    """

    if team == home_team:
        player = [{'name': name, 'id': players['Home'][name]['id']} for name in players['Home'].keys() if last_name in
                  name and players['Home'][name]['number'] == number]
    else:
        player = [{'name': name, 'id': players['Away'][name]['id']} for name in players['Away'].keys() if last_name in
                  name and players['Away'][name]['number'] == number]

    return player[0]


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
    return 'NA'


def which_zone(play_description):
    """
    Determine which zone the play occurred in (unless one isn't listed)
    :param play_description: the zone would be included here
    :return: Off, Def, Neu, or NA
    """
    s = [x.strip() for x in play_description.split(',')]  # Split by comma's into a list
    zone = [x for x in s if 'Zone' in x]  # Find if list contains which zone

    if not zone:
        return 'NA'

    if zone[0].find("Off") != -1:
        return 'Off'
    elif zone[0].find("Neu") != -1:
        return 'Neu'
    elif zone[0].find("Def") != -1:
        return 'Def'


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
        elif (y == 6 or y == 7) and td[0] != '#':
            # 6 & 7-> These are the player one ice one's
            # The second statement controls for when it's just a header

            baz = td[y].find_all('td')
            bar = [baz[z] for z in range(len(baz)) if
                   z % 4 != 0]  # Because of previous step we get repeats...so delete some

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
    soup = BeautifulSoup(html.content, 'html.parser')
    td = soup.select('td.+.bborder')

    # Create a list of lists (each length 8)...corresponds to 8 columns in html pbp
    td = [td[i:i + 8] for i in range(0, len(td), 8)]

    cleaned_html = [strip_html_pbp(x) for x in td]

    return cleaned_html


def get_event_players(event, players, home_team):
    """
    returns a dict with the players involved in the event
    :param event: fixed up html
    :param players: dict of players and id's
    :param home_team:
    :return: 
    """
    info = {
        'p1_name': '',
        'p1_ID': '',
        'p2_name': '',
        'p2_ID': '',
        'p3_name': '',
        'p3_ID': '',
    }
    description = event[5]
    ev_team = description[0]

    if ev_team == home_team:
        team_players = event[7]  # Player's on ice for team which had the event
        opp_players = event[6]  # Player's on ice for other team
    else:
        team_players = event[6]
        opp_players = event[7]

    description = description.split()
    description = [d for d in description if d != '' and d != ' ']

    if 'FAC' in event[4]:
        # Ex: NYR won Neu. Zone - N.J #14 HENRIQUE vs NYR #13 HAYES
        if ev_team == description[5]:
            p1 = get_player_name(description[7].upper(), description[6][1:], players, description[5], home_team)
            info['p1_name'] = p1['name']
            info['p1_ID'] = p1['id']
            p2 = get_player_name(description[7].upper(), description[6][1:], players, description[5], home_team)
            info['p2_name'] = p2['name']
            info['p2_ID'] = p2['id']
        else:
            p1 = get_player_name(description[11].upper(), description[10][1:], players, description[9], home_team)
            info['p1_name'] = p1['name']
            info['p1_ID'] = p1['id']
            p2 = get_player_name(description[7].upper(), description[6][1:], players, description[5], home_team)
            info['p2_name'] = p2['name']
            info['p2_ID'] = p2['id']
    elif 'SHOT' in event[4]:
        # Ex: NYR ONGOAL - #61 NASH, Wrist, Off. Zone, 50 ft.
        p = get_player_name(description[4][:-1].upper(), description[3][1:], players, description[0], home_team)
        info['p1_name'] = p['name']
        info['p1_ID'] = p['id']
    elif 'MISS' in event[4]:
        # N.J #38 FIDDLER, Tip-In, Wide of Net, Off. Zone, 12 ft.
        p = get_player_name(description[2][:-1].upper(), description[1][1:], players, description[0], home_team)
        info['p1_name'] = p['name']
        info['p1_ID'] = p['id']
    elif 'BLOCK' in event[4]:
        # NYR #8 KLEIN BLOCKED BY N.J #51 KALININ, Wrist, Def. Zone
        p1 = get_player_name(description[7][:-1].upper(), description[6][1:], players, description[5], home_team)
        info['p1_name'] = p1['name']
        info['p1_ID'] = p1['id']
        p2 = get_player_name(description[2].upper(), description[1][1:], players, description[0], home_team)
        info['p2_name'] = p2['name']
        info['p2_ID'] = p2['id']
    elif 'GOAL' in event[4]:
        # N.J #11 PARENTEAU(7), Tip-In, Off. Zone, 10 ft. Assists: #21 PALMIERI(11); #28 SEVERSON(13)
        description = [d for d in description if '(' in d or '#' in d]
        i = description[1].index('(')  # As to not include the parentheses in the player's name

        p1 = get_player_name(description[1][:i], description[0][1:], players, description[0], home_team)
        info['p1_name'] = p1['name']
        info['p1_ID'] = p1['id']

        if len(description) >= 4:
            # One Assist
            i = description[3].index('(')
            p2 = get_player_name(description[3][:i], description[2][1:], players, description[0], home_team)
            info['p2_name'] = p2['name']
            info['p2_ID'] = p2['id']

        if len(description) == 6:
            # Two Assists
            i = description[5].index('(')
            p3 = get_player_name(description[5][:i], description[4][1:], players, description[0], home_team)
            info['p3_name'] = p3['name']
            info['p3_ID'] = p3['id']

    elif 'PENL' in event[4]:
        # MTL #81 ELLER Hooking(2 min), Def. Zone Drawn By: TOR #11 SJOSTROM
        p1 = get_player_name(description[2], description[1][1:], players, description[0], home_team)
        info['p1_name'] = p1['name']
        info['p1_ID'] = p1['id']
        if 'By:' in description:
            i = description.index('By:')

            # If it's a penalty not drawn...the team isn't isn't after 'By:'
            if 'Served' not in description:
                p2 = get_player_name(description[i + 3].strip(','), description[i + 2][1:], players, description[i+1],
                                     home_team)
            else:
                p2 = get_player_name(description[i + 2].strip(','), description[i + 1][1:], players, description[0],
                                     home_team)
            info['p2_name'] = p2['name']
            info['p2_ID'] = p2['id']

    return info


def parseEvent_html(event, players, home_team, away_team, if_plays_in_json, current_score):
    """
    Receievs an event and parses it
    :param event: 
    :param players: players in game
    :param home_team:
    :param away_team:
    :param if_plays_in_json: If the pbp json contains the plays
    :param current_score: current score for both teams
    :return: dict with info
    """
    away_players = event[6]
    home_players = event[7]

    event_dict = dict()

    event_dict['Event'] = event[4]
    if event_dict['Event'] in ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'PENL', 'FAC', 'HIT', 'TAKE', 'GIVE']:
        event_dict['Ev_Team'] = event[5].split()[0]  # Split the description and take the first thing (which is the team)

    # If it's a goal change the score
    if event[4] == 'GOAL':
        if event_dict['Ev_Team'] == home_team:
            current_score['Home'] += 1
        else:
            current_score['Away'] += 1

    event_dict['Home_Score'] = current_score['Home']
    event_dict['Away_Score'] = current_score['Away']

    # Populate away and home player info
    for j in range(6):
        try:
            event_dict['awayPlayer{}'.format(j + 1)] = away_players[j][0].upper()
            event_dict['awayPlayer{}_id'.format(j + 1)] = players['Away'][away_players[j][0].upper()]['id']
        except (KeyError, IndexError):
            event_dict['awayPlayer{}'.format(j + 1)] = 'NA'
            event_dict['awayPlayer{}_id'.format(j + 1)] = 'NA'

        try:
            event_dict['homePlayer{}'.format(j + 1)] = home_players[j][0].upper()
            event_dict['homePlayer{}_id'.format(j + 1)] = players['Home'][home_players[j][0].upper()]['id']
        except (KeyError, IndexError):
            event_dict['homePlayer{}'.format(j + 1)] = 'NA'
            event_dict['homePlayer{}_id'.format(j + 1)] = 'NA'

    # Did this because above method assumes goalie is at end of player list
    for x in away_players:
        if x[2] == 'G':
            event_dict['Away_Goalie'] = x[0].upper()
        else:
            event_dict['Away_Goalie'] = 'NA'

    for x in home_players:
        if x[2] == 'G':
            event_dict['Home_Goalie'] = x[0].upper()
        else:
            event_dict['Home_Goalie'] = 'NA'

    event_dict['Away_Skaters'] = len(away_players)
    event_dict['Home_Skaters'] = len(home_players)

    try:
        home_skaters = event_dict['Home_Skaters'] - 1 if event_dict['Home_Goalie'] != 'NA' else len(home_players)
        away_skaters = event_dict['Away_Skaters'] - 1 if event_dict['Away_Goalie'] != 'NA' else len(away_players)
    except KeyError:
        # Getting a key error here means that home/away goalie isn't there..which means home/away players are empty
        home_skaters = 0
        away_skaters = 0

    event_dict['Strength'] = 'x'.join([str(home_skaters), str(away_skaters)])
    event_dict['Ev_Zone'] = which_zone(event[5])

    if 'PENL' in event[4]:
        event_dict['Type'] = get_penalty(event[5])
    else:
        event_dict['Type'] = shot_type(event[5]).upper()

    # If the json pbp is missing plays...we also do this stuff
    if if_plays_in_json:
        event_dict['Period'] = event[1]
        event_dict['Time_Elapsed'] = event[3]
        event_dict['Seconds_Elapsed'] = shared_functions.convert_to_seconds(event[3])
        event_dict['Description'] = event[5]

        print(event_dict['Event'], event_dict['Period'], event_dict['Time_Elapsed'])
        if event_dict['Event'] in ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'PENL', 'FAC', 'HIT', 'TAKE', 'GIVE']:
            event_dict.update(get_event_players(event, players, home_team))  # Add players involves in event
        """
        try:
            
        except Exception as e:
            print('Exception at ', event[5], e)
            event_dict['p1_name'] = ' '
            event_dict['p1_ID'] = ' '
            event_dict['p2_name'] = ' '
            event_dict['p2_ID'] = ' '
            event_dict['p3_name'] = ' '
            event_dict['p3_ID'] = ' '
        """

    return [event_dict, current_score]


def parse_html(html, players, home_team, away_team, if_plays_in_json):
    """
    Parse html game pbp
    :param html: 
    :param players: players in the game (from json pbp)
    :param home_team:
    :param away_team:
    :param if_plays_in_json: If the pbp json contains the plays
    :return: 
    """

    if if_plays_in_json:
        columns = ['Event', 'Type', 'Strength', 'Ev_Zone', 'awayPlayer1', 'awayPlayer1_id', 'awayPlayer2',
                   'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id', 'awayPlayer5',
                   'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id', 'homePlayer2',
                   'homePlayer2_id', 'homePlayer3', 'homePlayer3_id', 'homePlayer4', 'homePlayer4_id', 'homePlayer5',
                   'homePlayer5_id', 'homePlayer6', 'homePlayer6_id', 'Away_Goalie', 'Home_Goalie', 'Home_Score',
                   'Away_Score']
    else:
        columns = ['Period', 'Time_Elapsed', 'Seconds_Elapsed', 'Event', 'Description', 'Type', 'Ev_Team', 'Strength',
                   'p1_name', 'p1_ID', 'p2_name', 'p2_ID', 'p3_name', 'p3_ID', 'Ev_Zone', 'awayPlayer1',
                   'awayPlayer1_id',
                   'awayPlayer2', 'awayPlayer2_id', 'awayPlayer3', 'awayPlayer3_id', 'awayPlayer4', 'awayPlayer4_id',
                   'awayPlayer5', 'awayPlayer5_id', 'awayPlayer6', 'awayPlayer6_id', 'homePlayer1', 'homePlayer1_id',
                   'homePlayer2', 'homePlayer2_id', 'homePlayer3', 'homePlayer3_id', 'homePlayer4', 'homePlayer4_id',
                   'homePlayer5', 'homePlayer5_id', 'homePlayer6', 'homePlayer6_id', 'Away_Goalie', 'Home_Goalie',
                   'Home_Score', 'Away_Score']

    current_score = {'Home': 0, 'Away': 0}
    events, current_score = zip(*(parseEvent_html(event, players, home_team, away_team, if_plays_in_json, current_score)
                                  for event in html if event[0] != '#' and event[0] != 'GOFF'))

    return pd.DataFrame(list(events), columns=columns)


def scrapeGame(game_id):
    """
    Calls getPBP and scrapes the raw PBP json and HTML
    If one of the the pbp's (json or html) aren't there we return with nothing.
    Also if something is wrong with one of them (or they don't align) we return nothing.
    :param game_id: game to scrape
    :return: DataFrame of game info
    """
    try:
        game_html = getPBP_html(game_id)
    except requests.exceptions.HTTPError as e:
        print('Html pbp for game {} is not there'.format(game_id), e)
        return None

    try:
        teams = getTeams_html(game_html)
        html_df = parse_html(clean_html_pbp(game_html), {}, teams[0], teams[1],  False)
    except Exception as e:
        print('Error for html pbp for game {}'.format(game_id), e)
        return None

    return html_df


