"""
Scrape the PBP info for a given game
"""
import json
import time
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import hockey_scraper.utils.shared as shared
import hockey_scraper.utils.save_pages as sp

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.action_chains import ActionChains


options = Options()
options.add_argument("--headless")



def scrape_page(url):
    """

    :param url: Game pbp url

    :return n pages - each have period info
    """
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    time.sleep(8)

    """

    for _ in range(5):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(.2)
    #['SO', 'OT', 'OT1', 'OT2', '3', '2', '1']:


    for period in ['3', '2', '1']: 
        btn = '//a[@ng-click="ctrl.period = \'{}\'"]'.format(period)

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, btn)))
            #driver.find_element_by_xpath(btn).click()
            btn_elem = driver.find_element_by_xpath(btn)
            ActionChains(driver).move_to_element(btn_elem).click().perform()
        except (TimeoutException, ElementNotVisibleException, WebDriverException) as e:
            print(e)

        ### This just print the last row in the list to see if we are correctly toggling between periods
        soup = BeautifulSoup(driver.page_source, "lxml")
        plays_table = soup.find("table", {"class": "play-by-play"})
        plays = plays_table.find_all("tr")
        print(plays[-1])

    """

    pg = driver.page_source
    driver.close()

    return pg




def get_pbp(game_id):
    """
    Get the response for a game (e.g. https://www.nwhl.zone/stats#/100/game/268087/play-by-play)
    
    :param game_id: Given Game id (e.g. 268087)
    
    :return: 
    """
    file_info = {
        "url": 'https://www.nwhl.zone/stats#/100/game/{}/play-by-play'.format(game_id),
        "name": str(game_id),
        "type": "nwhl_json_pbp",
        "season": "nwhl",
        'dir': shared.docs_dir
    }
    
    # Saved pages logic is here bec. of button logic in scrape_pbp
    if shared.docs_dir and sp.check_file_exists(file_info) and not shared.re_scrape:
        # TODO: Regex matching game_id
        pgs = sp.get_page(file_info)
    else:
        pgs = scrape_page(file_info['url'])

        # We have to save each individually
        #for i, pg in enumerate(pgs):
        i=1
        file_info['name'] += "_{}".format(i)
        sp.save_page(pgs, file_info)

    return pgs






def parse_event(event, score, teams, date, game_id, players):
    """
    Parses a single event when the info is in a json format

    :param event: json of event 
    :param score: Current score of the game
    :param teams: Teams dict (id -> name)
    :param date: date of the game
    :param game_id: game id for game
    :param players: Dict of player ids to player names
    
    :return: dictionary with the info
    """
    play = dict()

    


def parse_json(game_json, game_id,):
    """
    Scrape the json for a game
    
    plus, minus players

    :param game_json: raw json
    :param game_id: game id for game

    :return: Either a DataFrame with info for the game 
    """
    cols = ['game_id', 'date', 'season', 'period', 'seconds_elapsed', 'event', 'ev_team', 'home_team', 'away_team',
            'p1_name', 'p1_id', 'p2_name', 'p2_id', 'p3_name', 'p3_id',
            "homePlayer1", "homePlayer1_id", "homePlayer2", "homePlayer2_id", "homePlayer3", "homePlayer3_id",
            "homePlayer4", "homePlayer4_id", "homePlayer5", "homePlayer5_id", "homePlayer6", "homePlayer6_id",
            "awayPlayer1", "awayPlayer1_id", "awayPlayer2", "awayPlayer2_id", "awayPlayer3", "awayPlayer3_id",
            "awayPlayer4", "awayPlayer4_id", "awayPlayer5", "awayPlayer5_id", "awayPlayer6", "awayPlayer6_id",
            'home_goalie', 'home_goalie_id', 'away_goalie', 'away_goalie_id', 'details', 'home_score', 'away_score',
            'xC', 'yC', 'play_index']

    # B4 anything - if there are no plays we leave
    if len(game_json['plays']) == 0:
        shared.print_error("The Json pbp for game {} contains no plays and therefore can't be parsed".format(game_id))
        return pd.DataFrame()

    # Get all the players in the game
    players = get_roster(game_json)

    # Initialize & Update as we go along
    score = {"home": 0, "away": 0}
    teams = {"home": {"id": game_json['game']['home_team'], "name": game_json['team_instance'][0]['abbrev']},
             "away": {"id": game_json['game']['away_team'], "name": game_json['team_instance'][1]['abbrev']}
             }

    # Get date from UTC timestamp
    date = game_json['plays'][0]['created_at']
    date = datetime.datetime.strptime(date[:date.rfind("-")], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

    try:
        events = [parse_event(play, score, teams, date, game_id, players) for play in game_json['plays']]
    except Exception as e:
        shared.print_error('Error parsing Json pbp for game {} {}'.format(game_id, e))
        return pd.DataFrame()

    df = pd.DataFrame(events, columns=cols)

    # Get rid of null events and order by play index
    df = df[(~pd.isnull(df['event'])) & (df['event'] != "")]
    df = df.sort_values(by=['play_index'])
    df = df.drop(['play_index'], axis=1)

    return df.reset_index(drop=True)


def scrape_pbp(game_id):
    """
    Scrape the pbp data for a given game
    
    :param game_id: Given Game id (e.g. 18507472)
    
    :return: DataFrame with pbp info
    """
    game_json = get_pbp(game_id)

    if not game_json:
        shared.print_error("Pbp for game {} is not either not there or can't be obtained".format(game_id))
        return pd.DataFrame()

    try:
        game_df = parse_json(game_json, game_id)
    except Exception as e:
        shared.print_error('Error parsing the Pbp for game {} {}'.format(game_id, e))
        return pd.DataFrame()

    return game_df

