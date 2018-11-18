"""
This module contains functions to scrape the json schedule for any games or date range
"""

import json
import time
import datetime
import hockey_scraper.shared as shared


def get_schedule(date_from, date_to):
    """
    Scrapes games in date range
    Ex: https://statsapi.web.nhl.com/api/v1/schedule?startDate=2010-10-03&endDate=2011-06-20
    
    :param date_from: scrape from this date
    :param date_to: scrape until this date
    
    :return: raw json of schedule of date range
    """
    page_info = {
        "url": 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}&endDate={b}'.format(a=date_from, b=date_to),
        "name": date_from + "_" + date_to,
        "type": "json_schedule",
        "season": shared.get_season(date_from),
    }

    return json.loads(shared.get_file(page_info))


def get_current_season():
    """
    Get Season based on today's date
    
    :return: season -> ex: 2016 for 2016-2017 season
    """
    year = str(datetime.date.today().year)
    date = time.strptime(str(datetime.date.today()), "%Y-%m-%d")

    if date > time.strptime('-'.join([year, '01-01']), "%Y-%m-%d"):
        if date < time.strptime('-'.join([year, '07-01']), "%Y-%m-%d"):
            return str(int(year)-1)
        else:
            return year
    else:
        if date > time.strptime('-'.join([year, '07-01']), "%Y-%m-%d"):
            return year
        else:
            return str(int(year)-1)


def get_dates(games):
    """
    Given a list game_ids it returns the dates for each game
    
    :param games: list with game_id's ex: 2016020001
    
    :return: list with game_id and corresponding date for all games
    """
    games.sort()

    year_from = str(games[0])[:4]
    year_to = str(games[len(games)-1])[:4]
    date_from = '-'.join([year_from, '9', '1'])      # Earliest games in sample

    # If the last game is part of the ongoing season then only request the schedule until that day...we get strange
    # errors if we don't do it like this
    if year_to == get_current_season():
        date_to = '-'.join([str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day)])
    else:
        date_to = '-'.join([str(int(year_to) + 1), '7', '1'])  # Newest game in sample

    # TODO: Assume true is live here -> Workaround
    schedule = scrape_schedule(date_from, date_to, preseason=True, live=True)
    games_list = []

    for game in schedule:
        if game['game_id'] in games:
            games_list.extend([game])

    return games_list


def scrape_schedule(date_from, date_to, preseason=False, live=False):
    """
    Calls getSchedule and scrapes the raw schedule Json
    
    :param date_from: scrape from this date
    :param date_to: scrape until this date
    :param preseason: Boolean indicating whether include preseason games (default if False)
    :param live: Boolean indicating whether we are scraping live games. Means we relax the requirement of checking if 
                 the game is over. 
    
    :return: list with all the game id's
    """
    schedule = []
    schedule_json = get_schedule(date_from, date_to)

    for day in schedule_json['dates']:
        for game in day['games']:
            if game['status']['detailedState'] == 'Final' or live:
                game_id = int(str(game['gamePk'])[5:])
                if (game_id >= 20000 or preseason) and game_id < 40000:
                    game_time = datetime.datetime.strptime(game['gameDate'][:-1], "%Y-%m-%dT%H:%M:%S")
                    schedule.append({"game_id": game['gamePk'], "date": day['date'], "start_time": game_time,
                                     "home_team": shared.get_team(game['teams']['home']['team']['name'].upper()),
                                     "away_team": shared.get_team(game['teams']['away']['team']['name'].upper()),
                                     "status": game["status"]["abstractGameState"]
                                     })

    return schedule
