from bs4 import BeautifulSoup
import requests

from scrape import shared


def get_roster(game_id):
    """
    Given a game_id it returns the raw html
    Ex: http://www.nhl.com/scores/htmlreports/20162017/RO020475.HTM

    :param game_id: the game
    :return: raw html of game
    """
    game_id = str(game_id)
    year = game_id[:4]
    url = 'http://www.nhl.com/scores/htmlreports/{}{}/RO{}.HTM'.format(
        year,
        int(year) + 1,
        game_id[4:])

    return shared.get_url(url)


def fix_name(player):
    """
    Sometimes a player had a (A) or (C) attached to their name
    :param player: list of player info -> [number, position, name]
    :return: fixed list
    """
    return player.replace(' (A)', '').replace(' (C)', '').strip()


def get_coaches(soup):
    """
    scrape head coaches
    :param soup: html
    :return:
    """
    coaches = soup.find('tr', {'id': "HeadCoaches"}).find_all('td')

    return {
        'Away': coaches[1].get_text(),
        'Home': coaches[3].get_text(),
    }


def process_players(table):
    """
    Parse players in a table

    :param table: BeautifulSoup table containing roster information
    :return: List of `[number, position, name]`
    """
    cells = [cell.get_text() for cell in table.find_all('td')]

    # Make list of list of 3 each. The three are: number, position, name (in that order)
    players = (cells[i:i + 3] for i in range(0, len(cells), 3))

    # Remove headers (starts with '#') and empty rows
    return [[number, position, fix_name(name)]
            for number, position, name in players
            if not (number == '\xa0' or number.startswith('#'))]


def get_players(soup):
    """
    scrape roster for players
    :param soup: html
    :return:
    """
    tables = soup.find_all(
        'table',
        {
            'align': 'center',
            'border': '0',
            'cellpadding': '0',
            'cellspacing': '0',
            'width': '100%'
        }
    )

    # There are 5 tables which correspond to the above criteria.
    # tables[0] is nothing
    # tables[1] is away starters
    # tables[2] is home starters
    # tables[3] is away scratches
    # tables[4] is home scratches

    away = process_players(tables[1]) + process_players(tables[3])
    home = process_players(tables[2]) + process_players(tables[4])

    return {'Away': away, 'Home': home}


def scrape_roster(game_id):
    """
    For a given game scrapes the roster
    :param game_id:
    :return: dict of players (home and away) an dict for both head coaches
    """

    try:
        roster = get_roster(game_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == requests.codes.not_found:
            raise Exception('Roster for game {} is not there'.format(game_id))

        raise Exception('Unknown error: {}'.format(e))

    try:
        soup = BeautifulSoup(roster.content, "html.parser")
        players = get_players(soup)
        head_coaches = get_coaches(soup)
    except Exception as e:
        raise Exception('Problem with playing roster for game {}: {}'.format(game_id, e))

    return {'players': players, 'head_coaches': head_coaches}
