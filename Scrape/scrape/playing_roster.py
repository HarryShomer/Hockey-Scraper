from bs4 import BeautifulSoup

from scrape import shared


def get_roster(game_id):
    """
    Given a game_id it returns the raw html
    Ex: http://www.nhl.com/scores/htmlreports/20162017/RO020475.HTM
    :param game_id: the game
    :return: raw html of game
    """
    game_id = str(game_id)
    url = 'http://www.nhl.com/scores/htmlreports/{}{}/RO{}.HTM'.format(game_id[:4], int(game_id[:4]) + 1, game_id[4:])

    return shared.get_url(url)


def fix_name(player):
    """
    Sometimes a player had a (A) or (C) attached to their name
    :param player: list of player info -> [number, position, name]
    :return: fixed list
    """
    player[2] = player[2][:player[2].find('(')]
    player[2] = player[2].strip()

    return player


def get_coaches(soup):
    """
    scrape head coaches
    :param soup: html
    :return:
    """
    head_coaches = dict()

    coaches = soup.find_all('tr', {'id': "HeadCoaches"})
    coaches = coaches[0].find_all('td')
    head_coaches['Away'] = coaches[1].get_text()
    head_coaches['Home'] = coaches[3].get_text()

    return head_coaches


def get_players(soup):
    """
    scrape roster for players
    :param soup: html
    :return:
    """
    players = dict()

    tables = soup.findAll('table', {'align': 'center', 'border': '0', 'cellpadding': '0', 'cellspacing': '0', 'width': '100%'})
    """
    There are 5 tables which correspond to the above criteria.
    tables[0] is nothing
    tables[1] is away starters
    tables[2] is home starters
    tables[3] is away scratches
    tables[4] is home scratches
    """

    away_starters = tables[1].find_all('td')
    away_scratches = tables[3].find_all('td')
    home_starters = tables[2].find_all('td')
    home_scratches = tables[4].find_all('td')

    away_starters = [i.get_text() for i in away_starters]
    away_scratches = [i.get_text() for i in away_scratches]
    home_starters = [i.get_text() for i in home_starters]
    home_scratches = [i.get_text() for i in home_scratches]

    # Make list of list of 3 each. The three are: number, position, name (in that order)
    away_starters = [away_starters[i:i + 3] for i in range(0, len(away_starters), 3)]
    away_scratches = [away_scratches[i:i + 3] for i in range(0, len(away_scratches), 3)]
    home_starters = [home_starters[i:i + 3] for i in range(0, len(home_starters), 3)]
    home_scratches = [home_scratches[i:i + 3] for i in range(0, len(home_scratches), 3)]

    # Get rid of header column
    away_starters = [i for i in away_starters if i[0] != '#']
    away_scratches = [i for i in away_scratches if i[0] != '#']
    home_starters = [i for i in home_starters if i[0] != '#']
    home_scratches = [i for i in home_scratches if i[0] != '#']

    away_players = away_starters + away_scratches
    home_players = home_starters + home_scratches

    # For those with (A) or (C) in name field get rid of it
    # first condition is to control when we get whitespace as one of the indices
    players['Away'] = [fix_name(i) if i[0] != '\xa0' and i[2].find('(') != -1 else i for i in away_players]
    players['Home'] = [fix_name(i) if i[0] != '\xa0' and i[2].find('(') != -1 else i for i in home_players]

    # Get rid when just whitespace
    players['Away'] = [i for i in away_players if i[0] != '\xa0']
    players['Home'] = [i for i in home_players if i[0] != '\xa0']

    return players


def scrape_roster(game_id):
    """
    For a given game scrapes the roster
    :param game_id:
    :return: dict of players (home and away) an dict for both head coaches
    """

    try:
        roster = get_roster(game_id)
    except Exception as e:
        print('Roster for game {} is not there'.format(game_id), e)
        raise Exception

    try:
        soup = BeautifulSoup(roster.content, "html.parser")
        players = get_players(soup)
        head_coaches = get_coaches(soup)
    except Exception as e:
        print('Problem with playing roster for game {}'.format(game_id), e)
        raise Exception

    return {'players': players, 'head_coaches': head_coaches}
