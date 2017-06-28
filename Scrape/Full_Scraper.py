import PBP_Scraper as pbp
import Shift_Scraper as shift
import pandas as pd


def scrape_game(game_id):
    """
    scrape both pbp and shifts
    :param game_id: game 
    :return: 
    """
    shift_df = shift.scrapeGame(game_id)
    pbp_df = pbp.scrapeGame(game_id)

    pbp_df.to_csv('bar.csv', sep=',')

    return [pbp_df, shift_df]


def scrapeYear(year):
    """
    Redefining how scrapeYear is in both the shift and PBP
    
    Calls scrapeSchedule to get the game_id's to scrape and then calls scrapeGame and combines
    all the scraped games into one DataFrame
    :param year: year to scrape
    :return: 
    """
    schedule=pbp.scrapeSchedule(year)
    season_df=pd.DataFrame()

    for game in schedule:
        frames = scrape_game(game)
        season_pbp_df=season_pbp_df.append(frames[0])
        season_shift_df = season_shift_df.append(frames[1])

"""Test"""

import time

start = time.time()
print(20001)
scrape_game(2010020001)

end = time.time()
print(end - start)
