"""Test for 'playing_roster.py'"""

import pytest

from hockey_scraper.nhl import playing_roster


@pytest.fixture
def scraped_roster():
    return playing_roster.scrape_roster("2016020475")


def test_fix_name():
    """ Tests to see that it takes the assistant captain and regular captain ('(A)' and '(C)') out of player's names."""
    assert playing_roster.fix_name(['27', 'D', 'RYAN MCDONAGH  (C)', False]) == ['27', 'D', 'RYAN MCDONAGH', False]
    assert playing_roster.fix_name(['5', 'D', 'DAN GIRARDI  (A)', False]) == ['5', 'D', 'DAN GIRARDI', False]
    assert playing_roster.fix_name(['13', 'R', 'KEVIN HAYES', False]) == ['13', 'R', 'KEVIN HAYES', False]


def test_get_players(scraped_roster):
    """ Tests if it get the correct players for both teams in the correct format. """
    home_roster = [
        ['5', 'D', 'DAN GIRARDI', False],
        ['8', 'D', 'KEVIN KLEIN', False],
        ['10', 'C', 'J.T. MILLER', False],
        ['12', 'L', 'MATT PUEMPEL', False],
        ['13', 'R', 'KEVIN HAYES', False],
        ['18', 'D', 'MARC STAAL', False],
        ['19', 'R', 'JESPER FAST', False],
        ['20', 'C', 'CHRIS KREIDER', False],
        ['21', 'C', 'DEREK STEPAN', False],
        ['22', 'D', 'NICK HOLDEN', False],
        ['24', 'C', 'OSCAR LINDBERG', False],
        ['26', 'L', 'JIMMY VESEY', False],
        ['27', 'D', 'RYAN MCDONAGH', False],
        ['36', 'C', 'MATS ZUCCARELLO', False],
        ['40', 'R', 'MICHAEL GRABNER', False],
        ['46', 'L', 'MAREK HRIVIK', False],
        ['61', 'L', 'RICK NASH', False],
        ['76', 'D', 'BRADY SKJEI', False],
        ['30', 'G', 'HENRIK LUNDQVIST', False],
        ['32', 'G', 'ANTTI RAANTA', False],
        ['4', 'D', 'ADAM CLENDENING', True],
        ['73', 'C', 'BRANDON PIRRI', True]
    ]
    away_roster = [
        ['2', 'D', 'JOHN MOORE', False],
        ['6', 'D', 'ANDY GREENE', False],
        ['7', 'D', 'JON MERRILL', False],
        ['8', 'R', 'BEAU BENNETT', False],
        ['9', 'L', 'TAYLOR HALL', False],
        ['11', 'R', 'PA PARENTEAU', False],
        ['12', 'D', 'BEN LOVEJOY', False],
        ['13', 'L', 'MICHAEL CAMMALLERI', False],
        ['14', 'C', 'ADAM HENRIQUE', False],
        ['19', 'C', 'TRAVIS ZAJAC', False],
        ['21', 'C', 'KYLE PALMIERI', False],
        ['22', 'D', 'KYLE QUINCEY', False],
        ['28', 'D', 'DAMON SEVERSON', False],
        ['36', 'R', 'NICK LAPPIN', False],
        ['37', 'C', 'PAVEL ZACHA', False],
        ['38', 'L', 'VERNON FIDDLER', False],
        ['44', 'L', 'MILES WOOD', False],
        ['51', 'C', 'SERGEY KALININ', False],
        ['1', 'G', 'KEITH KINKAID', False],
        ['35', 'G', 'CORY SCHNEIDER', False],
        ['16', 'C', 'JACOB JOSEFSON', True],
        ['20', 'L', 'LUKE GAZDIC', True],
        ['25', 'R', 'DEVANTE SMITH-PELLY', True]
    ]

    assert 'Home' in scraped_roster['players']
    assert 'Away' in scraped_roster['players']

    assert scraped_roster['players']['Home'] == home_roster
    assert scraped_roster['players']['Away'] == away_roster


def test_get_coaches(scraped_roster):
    """ Tests if it get the correct coaches for both teams in the correct format. """
    assert 'Home' in scraped_roster['head_coaches']
    assert 'Away' in scraped_roster['head_coaches']

    assert scraped_roster['head_coaches']['Home'] == 'ALAIN VIGNEAULT'
    assert scraped_roster['head_coaches']['Away'] == 'JOHN HYNES'


def test_scrape_roster(scraped_roster):
    """ Test scraping all the roster info """
    assert 'players' in scraped_roster
    assert 'head_coaches' in scraped_roster
