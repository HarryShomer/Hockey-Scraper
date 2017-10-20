import pandas as pd
from bs4 import BeautifulSoup
import time
import hockey_scraper.shared as shared


def get_teams(soup):
    """
    Return the team for the TOI tables and the home team
    :param soup: souped up html
    :return: list with team and home team
    """
    import re

    team = soup.find('td', class_='teamHeading + border')  # Team for shifts
    team = team.get_text()

    # Get Home Team
    teams = soup.find_all('td', {'align': 'center', 'style': 'font-size: 10px;font-weight:bold'})
    regex = re.compile(r'>(.*)<br/>')
    home_team = regex.findall(str(teams[7]))

    return [team, home_team[0]]


def analyze_shifts(shift, name, team, home_team, player_ids):
    """
    Analyze shifts for each player when using.
    Prior to this each player (in a dictionary) has a list with each entry being a shift.
    This function is only used for the html
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
    shifts['Team'] = shared.TEAMS[team.strip(' ')]
    shifts['Start'] = shared.convert_to_seconds(shift[2].split('/')[0])
    shifts['End'] = shared.convert_to_seconds(shift[3].split('/')[0])
    shifts['Duration'] = shared.convert_to_seconds(shift[4].split('/')[0])

    try:
        if home_team == team:
            shifts['Player_Id'] = player_ids['Home'][name.upper()]['id']
        else:
            shifts['Player_Id'] = player_ids['Away'][name.upper()]['id']
    except KeyError:
        shifts['Player_Id'] = ''

    return shifts


def get_shifts(game_id):
    """
    Given a game_id it returns a DataFrame with the shifts for both teams
    Ex: http://www.nhl.com/scores/htmlreports/20162017/TV020971.HTM
    :param game_id: the game
    :return: DataFrame with all shifts, return None when an exception is thrown when parsing
    """
    game_id = str(game_id)
    home_url = 'http://www.nhl.com/scores/htmlreports/{}{}/TH{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])
    away_url = 'http://www.nhl.com/scores/htmlreports/{}{}/TV{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])

    home = shared.get_url(home_url)
    time.sleep(1)

    away = shared.get_url(away_url)
    time.sleep(1)

    return home, away


def parse_html(html, player_ids, game_id):
    """
    Parse the html
    :param html: cleaned up html
    :param player_ids: dict of home and away players
    :param game_id: id for game
    :return: DataFrame with info
    """
    columns = ['Game_Id', 'Player', 'Player_Id', 'Period', 'Team', 'Start', 'End', 'Duration']
    df = pd.DataFrame(columns=columns)

    soup = BeautifulSoup(html.content, "lxml")

    teams = get_teams(soup)
    team = teams[0]
    home_team = teams[1]

    td = soup.findAll(True, {'class': ['playerHeading + border', 'lborder + bborder']})

    """
    The list 'td' is laid out with player name followed by every component of each shift. Each shift contains: 
    shift #, Period, begin, end, and duration. The shift event isn't included. 
    """
    players = dict()
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

        shifts = [analyze_shifts(shift, key, team, home_team, player_ids) for shift in players[key]['Shifts']]
        df = df.append(shifts, ignore_index=True)

    df['Game_Id'] = str(game_id)[5:]
    return df


def scrape_game(game_id, players):
    """
    Scrape the game.
    Try the json first, if it's not there do the html (it should be there for all games)
    :param game_id: id for game
    :param players: list of players
    :return: DataFrame with info for the game
    """
    home_html, away_html = get_shifts(game_id)

    away_df = parse_html(away_html, players, game_id)
    home_df = parse_html(home_html, players, game_id)

    game_df = pd.concat([away_df, home_df], ignore_index=True)

    game_df = game_df.sort_values(by=['Period', 'Start'], ascending=[True, True])  # Sort by period and by time
    game_df = game_df.reset_index(drop=True)

    return game_df



