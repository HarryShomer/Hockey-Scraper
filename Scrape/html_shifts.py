import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import shared_functions


def analyze_shifts(shift, name, team, home_team, player_ids):
    """
    Analyze shifts for each player when using.
    Prior to this each player (in a dictionary) has a list with each entry being a shift.
    This function is only used for the html
    :param shift: 
    :param name: 
    :param team: 
    :param home_team:
    :param player_ids:
    :return: dict with info for shift
    """
    shifts = dict()

    shifts['Player'] = name.upper()
    shifts['Period'] = '4' if shift[1] == 'OT' else shift[1]
    shifts['Team'] = shared_functions.TEAMS[team.strip(' ')]
    shifts['Start'] = shared_functions.convert_to_seconds(shift[2].split('/')[0])
    shifts['End'] = shared_functions.convert_to_seconds(shift[3].split('/')[0])
    shifts['Duration'] = shared_functions.convert_to_seconds(shift[4].split('/')[0])

    if home_team == team:
        shifts['Player_Id'] = player_ids['Home'][name.upper()]['id']
    else:
        shifts['Player_Id'] = player_ids['Away'][name.upper()]['id']

    return shifts


def get_shifts(game_id, players):
    """
    Given a game_id it returns a DataFrame with the shifts for both teams
    :param game_id: the game
    :param players: list of players
    :return: DataFrame with all shifts, return None when an exception is thrown when parsing
    http://www.nhl.com/scores/htmlreports/20162017/TV020971.HTM
    """
    game_id = str(game_id)
    home_url = 'http://www.nhl.com/scores/htmlreports/{}{}/TH{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])
    away_url = 'http://www.nhl.com/scores/htmlreports/{}{}/TV{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])

    home = requests.get(home_url)
    home.raise_for_status()
    time.sleep(1)

    away = requests.get(away_url)
    away.raise_for_status()
    time.sleep(1)

    away_df = parse_html(away, players)
    home_df = parse_html(home, players)

    game_df = pd.concat([away_df, home_df], ignore_index=True)

    game_df = game_df.sort_values(by=['Period', 'Start'], ascending=[True, True])  # Sort by period and by time
    game_df = game_df.reset_index(drop=True)

    return game_df


def parse_html(html, player_ids):
    """
    Parse the html
    :param html: raw html
    :param player_ids: dict of home and away players
    :return: DataFrame with info
    """
    columns=['Player', 'Player_Id', 'Period', 'Team', 'Start', 'End', 'Duration']
    df= pd.DataFrame(columns=columns)

    soup = BeautifulSoup(html.content, 'html.parser')
    team = soup.find('td', class_='teamHeading + border')       # Team for shifts
    team = team.get_text()

    # Get Home Team
    teams = soup.find_all('td', {'align': 'center', 'style': 'font-size: 10px;font-weight:bold'})
    home_team = teams[7].get_text()
    home_team = home_team[:home_team.index('Game')]

    td = soup.findAll(True, {'class': ['playerHeading + border', 'lborder + bborder']})

    """
    The list 'td' is laid out with player name followed by every component of each shift. Each shift contains: 
    shift #, Period, begin, end, and duration. The shift event isn't included. 
    """
    players = dict()
    for t in td:
        t=t.get_text()
        if ',' in t:     # If it has a comma in it we know it's a player's name...so add player to dict
            name=t
            # Just format the name normally...it's coded as: 'num last_name, first_name'
            name = name.split(',')
            name = ' '.join([name[1].strip(' '), name[0][2:].strip(' ')])
            players[name] = dict()
            players[name]['number'] = name[0][:2].strip()
            players[name]['Shifts'] = []
        else:
            # Here we add all the shifts to whatever player we are up to
            players[name]['Shifts'].extend([t])

    for key in players.keys():
        # Create a list of lists (each length 5)...corresponds to 5 columns in html shifts
        players[key]['Shifts'] = [players[key]['Shifts'][i:i + 5] for i in range(0, len(players[key]['Shifts']), 5)]

        shifts = [analyze_shifts(shift, key, team, home_team, player_ids) for shift in players[key]['Shifts']]
        df = df.append(shifts, ignore_index=True)

    return df


def scrape_game(game_id, player_ids):
    """
    Scrape the game.
    Try the json first, if it's not there do the html (it should be there for all games)
    :param game_id: game
    :param player_ids: dict of home and away players
    :return: DataFrame with info for the game
    """
    game_df = get_shifts(game_id, player_ids)

    return game_df




