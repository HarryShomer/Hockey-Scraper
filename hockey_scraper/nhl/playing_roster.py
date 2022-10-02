"""
This module contains functions to scrape the Html game roster for any given game
"""

from bs4 import BeautifulSoup
import hockey_scraper.utils.shared as shared


def get_roster(game_id):
    """
    Given a game_id it returns the raw html
    Ex: http://www.nhl.com/scores/htmlreports/20162017/RO020475.HTM
    
    :param game_id: the game
    
    :return: raw html of game
    """
    game_id = str(game_id)

    page_info = {
        "url": 'http://www.nhl.com/scores/htmlreports/{}{}/RO{}.HTM'.format(game_id[:4], int(game_id[:4]) + 1, game_id[4:]),
        "name": game_id,
        "type": "html_roster",
        "season": game_id[:4],
    }

    return shared.get_file(page_info)


def get_content(roster):
    """
    Uses Beautiful soup to parses the html document.
    Some parsers work for some pages but don't work for others....I'm not sure why so I just try them all here in order
    
    :param roster: doc
    
    :return: players and coaches
    """
    parsers = ["lxml", "html.parser", "html5lib"]

    for parser in parsers:
        soup = BeautifulSoup(roster, "lxml")
        players = get_players(soup)
        head_coaches = get_coaches(soup)

        if len(players) > 0:
            break

    return players, head_coaches


def fix_name(player):
    """
    Get rid of (A) or (C) when a player has it attached to their name
    
    :param player: list of player info -> [number, position, name]
    
    :return: fixed list
    """
    if player[2].find('(A)') != -1:
        player[2] = player[2][:player[2].find('(A)')].strip()
    elif player[2].find('(C)') != -1:
        player[2] = player[2][:player[2].find('(C)')].strip()

    return player


def get_coaches(soup):
    """
    scrape head coaches
    
    :param soup: html
    
    :return: dict of coaches for game
    """
    coaches = soup.find_all('tr', {'id': "HeadCoaches"})

    # If it picks up nothing just return the empty list
    if not coaches:
        return coaches

    coaches = coaches[0].find_all('td')

    return {
        'Away': coaches[1].get_text(),
        'Home': coaches[3].get_text()
    }


def get_players(soup):
    """
    scrape roster for players 
    
    :param soup: html
    
    :return: dict for home and away players
    """
    tables = soup.findAll('table', {'align': 'center', 'border': '0', 'cellpadding': '0', 'cellspacing': '0', 'width': '100%'})

    # If it picks up nothing just return the empty list
    if not tables:
        return tables

    """
    There are 5 tables which correspond to the above criteria.
    tables[0] is nothing
    tables[1] is away starters
    tables[2] is home starters
    tables[3] is away scratches
    tables[4] is home scratches
    """

    del tables[0]
    player_info = [table.find_all('td') for table in tables]

    player_info = [[x.get_text() for x in group] for group in player_info]

    # Make list of list of 3 each. The three are: number, position, name (in that order)
    player_info = [[group[i:i+3] for i in range(0, len(group), 3)] for group in player_info]

    # Get rid of header column
    player_info = [[player for player in group if player[0] != '#'] for group in player_info]

    # Add whether the player was a scratch
    # 2 and 3 hold the scratches
    for i in range(len(player_info)):
        for j in range(len(player_info[i])):
            if i == 2 or i == 3:
                player_info[i][j].append(True)
            else:
                player_info[i][j].append(False)

    players = {'Away': player_info[0], 'Home': player_info[1]}

    # Scratches aren't always included
    if len(player_info) == 4:
        players['Away'] += player_info[2]
        players['Home'] += player_info[3]

    # For those with (A) or (C) in name field get rid of it
    # First condition is to control when we get whitespace as one of the indices
    players['Away'] = [fix_name(i) if i[0] != u'\xa0' else i for i in players['Away']]
    players['Home'] = [fix_name(i) if i[0] != u'\xa0' else i for i in players['Home']]

    # Get rid when just whitespace
    players['Away'] = [i for i in players['Away'] if i[0] != u'\xa0']
    players['Home'] = [i for i in players['Home'] if i[0] != u'\xa0']

    return players


def scrape_roster(game_id):
    """
    For a given game scrapes the roster
    
    :param game_id: id for game
    
    :return: dict of players (home and away) an dict for both head coaches 
    """
    roster = get_roster(game_id)

    if not roster:
        shared.print_error("Roster for game {} is either not there or can't be obtained".format(game_id))
        return None

    try:
        players, head_coaches = get_content(roster)
    except Exception as e:
        shared.print_error('Error parsing Roster for game {} {}'.format(game_id, e))
        return None

    
    return {'players': players, 'head_coaches': head_coaches}
