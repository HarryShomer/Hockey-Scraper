"""
This module contains functions to scrape the Html Toi Tables (or shifts) for any given game
"""

import re
import pandas as pd
from bs4 import BeautifulSoup
import hockey_scraper.utils.shared as shared


def get_shifts(game_id):
    """
    Given a game_id it returns a the shifts for both teams
    Ex: http://www.nhl.com/scores/htmlreports/20162017/TV020971.HTM
    
    :param game_id: the game
    
    :return: Shifts or None
    """
    game_id = str(game_id)
    venue_pgs = tuple()

    for venue in ["home", "away"]:
        venue_tag = "H" if venue == "home" else "V"
        venue_url = 'http://www.nhl.com/scores/htmlreports/{}{}/T{}{}.HTM'.format(game_id[:4], int(game_id[:4])+1, venue_tag, game_id[4:])
  
        page_info = {
            "url": venue_url,
            "name": game_id,
            "type": "html_shifts_{}".format(venue),
            "season": game_id[:4],
        }

        venue_pgs += (shared.get_file(page_info), )

    return venue_pgs


def get_soup(shifts_html):
    """
    Uses Beautiful soup to parses the html document.
    Some parsers work for some pages but don't work for others....I'm not sure why so I just try them all here in order
    
    :param shifts_html: html doc
    
    :return: "soupified" html and player_shifts portion of html (it's a bunch of td tags)
    """
    parsers = ["lxml", "html.parser", "html5lib"]

    for parser in parsers:
        soup = BeautifulSoup(shifts_html, parser)
        td = soup.findAll(True, {'class': ['playerHeading + border', 'lborder + bborder']})

        if len(td) > 0:
            break

    return td, get_teams(soup)


def get_teams(soup):
    """
    Return the team for the TOI tables and the home team
    
    :param soup: souped up html
    
    :return: list with team and home team
    """
    team = soup.find('td', class_='teamHeading + border')  # Team for shifts
    team = team.get_text()

    # Get Home Team
    teams = soup.find_all('td', {'align': 'center', 'style': 'font-size: 10px;font-weight:bold'})
    regex = re.compile(r'>(.*)<br/?>')
    home_team = regex.findall(str(teams[7]))

    return [team, home_team[0]]


def analyze_shifts(shift, name, team, home_team, player_ids):
    """
    Analyze shifts for each player when using.
    Prior to this each player (in a dictionary) has a list with each entry being a shift.

    :param shift: info on shift
    :param name: player name
    :param team: given team
    :param home_team: home team for given game
    :param player_ids: dict with info on players
    
    :return: dict with info for shift
    """
    shifts = dict()

    shifts['Player'] = name.upper()
    shifts['Period'] = '4' if shift[1] == 'OT' else shift[1]
    shifts['Team'] = shared.get_team(team.strip(' '))
    shifts['Start'] = shared.convert_to_seconds(shift[2].split('/')[0])
    shifts['Duration'] = shared.convert_to_seconds(shift[4].split('/')[0])

    # I've had problems with this one...if there are no digits the time is fucked up
    if re.compile('\d+').findall(shift[3].split('/')[0]):
        shifts['End'] = shared.convert_to_seconds(shift[3].split('/')[0])
    else:
        shifts['End'] = shifts['Start'] + shifts['Duration']

    try:
        if home_team == team:
            shifts['Player_Id'] = player_ids['Home'][name.upper()]['id']
        else:
            shifts['Player_Id'] = player_ids['Away'][name.upper()]['id']
    except KeyError:
        shifts['Player_Id'] = None

    return shifts


def parse_html(html, player_ids, game_id):
    """
    Parse the html
    
    Note: Don't fuck with this!!! I'm not exactly sure how or why but it works. 
    
    :param html: cleaned up html
    :param player_ids: dict of home and away players
    :param game_id: id for game
    
    :return: DataFrame with info
    """
    all_shifts = []
    columns = ['Game_Id', 'Player', 'Player_Id', 'Period', 'Team', 'Start', 'End', 'Duration']

    td, teams = get_soup(html)

    team = teams[0]
    home_team = teams[1]
    players = dict()

    # The list 'td' is laid out with player name followed by every component of each shift. Each shift contains:
    # shift #, Period, begin, end, and duration. The shift event isn't included.
    for t in td:
        t = t.get_text()
        if ',' in t:     # If it has a comma in it we know it's a player's name...so add player to dict
            name = t
            # Just format the name normally...it's coded as: 'num last_name, first_name'
            name = name.split(',')
            name = ' '.join([name[1].strip(' '), name[0][2:].strip(' ')])
            name = shared.fix_name(name)
            players[name] = dict()
            players[name]['number'] = name[0][:2].strip()
            players[name]['Shifts'] = []
        else:
            # Here we add all the shifts to whatever player we are up to
            players[name]['Shifts'].extend([t])

    for key in players.keys():
        # Create a list of lists (each length 5)...corresponds to 5 columns in html shifts
        players[key]['Shifts'] = [players[key]['Shifts'][i:i + 5] for i in range(0, len(players[key]['Shifts']), 5)]

        # Parse each shift
        shifts = [analyze_shifts(shift, key, team, home_team, player_ids) for shift in players[key]['Shifts']]
        all_shifts.extend(shifts)

    df = pd.DataFrame(all_shifts)
    df['Game_Id'] = str(game_id)[5:]
    
    return df[columns]


def scrape_game(game_id, players):
    """
    Scrape the game. 
    
    :param game_id: id for game
    :param players: list of players
    
    :return: DataFrame with info for the game
    """
    columns = ['Game_Id', 'Period', 'Team', 'Player', 'Player_Id', 'Start', 'End', 'Duration']

    home_html, away_html = get_shifts(game_id)

    if home_html is None or away_html is None:
        shared.print_error("Html shifts for game {} is either not there or can't be obtained".format(game_id))
        return pd.DataFrame()

    try:
        away_df = parse_html(away_html, players, game_id)
        home_df = parse_html(home_html, players, game_id)
    except Exception as e:
        shared.print_error('Error parsing Html shifts for game {} {}'.format(game_id, e))
        return pd.DataFrame()

    # Combine the two
    game_df = pd.concat([away_df, home_df], ignore_index=True)
    game_df = pd.DataFrame(game_df, columns=columns)
    game_df = game_df.sort_values(by=['Period', 'Start'], ascending=[True, True])

    return game_df.reset_index(drop=True)
