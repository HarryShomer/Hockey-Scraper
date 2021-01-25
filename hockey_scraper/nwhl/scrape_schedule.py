"""
Scrape the schedule info for nwhl games
"""
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup
import hockey_scraper.utils.shared as shared
import hockey_scraper.utils.save_pages as sp

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")



def scrape_dynamic(url):
    """
    Dynamically scrape a given url and scroll down.

    :param url: Page to get

    :return source page
    """
    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    time.sleep(5)

    # Scroll down to get all the games - Do it a few times to make sure
    for _ in range(5):
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(.2)

    pg = browser.page_source
    browser.close()

    return pg


def get_schedule(url, name):
    """
    Given a url it returns the raw html

    :param url: url for page
    :param name: Name for saved file

    :return: raw html of game
    """
    file_info = {
        "url": url,
        "name": str(name) + "_schedule",
        "type": "html_schedule_nwhl",
        "season": "nwhl",
        'dir': shared.docs_dir
    }

    # Done manually due to custom scraping logic
    if shared.docs_dir and sp.check_file_exists(file_info) and not shared.re_scrape:
        pg =  sp.get_page(file_info)
    else:
        pg = scrape_dynamic(file_info['url'])
        sp.save_page(pg, file_info)

    return pg


def get_season_codes():
    """
    They use fucked up codes instead of actual years to represent seasons in the url.

    e.g. For 2019 - https://www.nwhl.zone/stats#/100/schedule?all&season_id=1950

    Instead of hardcoding it I just ping the base page and get the codes

    :return dict - season -> season_code
    """
    seed_url = 'https://www.nwhl.zone/stats#/100/schedule'

    pg = get_schedule(seed_url, "seed")
    soup = BeautifulSoup(pg, "lxml")

    # This grabs the options in the season dropdown
    filters = soup.find_all("div", {"class": "filters d"})
    selects = filters[0].find_all("select")
    options = selects[0].find_all("option")

    # Parses out the season and associated code for each
    season_codes = {}
    for o in options:
        season_codes[o['label'][:4]] = o['value'][o['value'].find(":")+1:]

    return season_codes


def parse_game(game, season):
    """
    Given a soup object for a given game parse out the info.

    Skip over all-star game

    :param games: Soup object
    :param season: nwhl season

    :return dict of info
    """
    parsed_game = {}

    # Team info
    teams = game.find_all("span", {"class": "team-inline"})

    if "All-Star" in teams[0].text:
        return parsed_game

    parsed_game['away_team'] = teams[0].find("span").text
    parsed_game['home_team'] = teams[1].find("span").text

    # Scores
    # If we don't puckey anything up the game hasn't occured yet 
    scores = game.find("td", {"class": "center"})
    team_scores = scores.find_all("span", {"class": re.compile("ng-binding.*")})
    parsed_game['away_score'] = None if not team_scores else team_scores[0].text
    parsed_game['home_score'] = None if not team_scores else team_scores[1].text

    # Date & Time
    dt_time = game.find_all("td", {"class": "center ng-binding"})
    date = dt_time[0].text
    parsed_game['game_time'] = dt_time[1].text

    # Date is structured as 'Sat Mar 5' 
    # So we pull month and date and infer year from date and season (use july as cutoff)
    num_month = time.strptime(date[4:7],'%b').tm_mon
    year = season if num_month >= 7 else season + 1
    parsed_game['date'] = f"{year}-{num_month}-{date[8:]}"

    ### Game id - link is structured like '#/100/game/274708'
    links = game.find("a")
    parsed_game['game_id'] = re.findall(".*\/(\d+)$", links['href'])[0]

    return parsed_game


def get_season_games(season, season_code):
    """
    For a given season get the schedule page and parse out the info for each game

    :param season: Season we are scraping
    :param season_code: season_id code for url param

    :return list of dicts with game info
    """
    parsed_games = []

    url = "https://www.nwhl.zone/stats#/100/schedule?season_id={}&all".format(season_code)
    pg = get_schedule(url, season)
    soup = BeautifulSoup(pg, "lxml")

    ## Each <tr> is a game
    sched = soup.find_all("table", {"class": "schedule"})[0]
    games = sched.find_all("tr", {"class": re.compile("^ng-scope")})

    for game in games:
        g = parse_game(game, season)
        if g:
            parsed_games.append(g)

    return parsed_games


def scrape_dates(from_date, to_date):
    """
    Get all the games between two dates. We scrape the schedule for each season in the 
    srange and then pick out the correct ones by date.
    
    :param from_date: Date Scrape from
    :param to_date: Date scrape to
    
    :return: List of all games
    """
    games = []

    season_codes = get_season_codes()
    first_season = shared.get_season(from_date)
    last_season = shared.get_season(to_date)

    # Convert to datetime to easily compare to game dates
    from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
    to_datetime = datetime.strptime(to_date, "%Y-%m-%d")

    for season in range(first_season, last_season+1):
        for game in get_season_games(season, season_codes[str(season)]):

            game_date = datetime.strptime(game['date'], "%Y-%m-%d")
            if from_datetime <= game_date <= to_datetime:
                games.append(game)

    return games


def scrape_season(season):
    """
    Scrape the games for a given season

    :param season: e.g. 2017

    :return list of dict of game info
    """
    season_codes = get_season_codes()
    return get_season_games(season, season_codes[str(season)])



