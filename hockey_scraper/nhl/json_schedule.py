"""
This module contains functions to scrape the json schedule for any games or date range
"""
import json
from datetime import datetime, timedelta
import hockey_scraper.utils.shared as shared

from tqdm import tqdm


# TODO: Currently rescraping page each time since the status of some games may have changed
# (e.g. Scraped on 2020-01-20 and game on 2020-01-21 was not Final...when use old page again will still think not Final)
# Need to find a more elegant way of doing this (Metadata???)
def get_schedule(date):
    """
    Scrapes games in date range
    Ex: https://api-web.nhle.com/v1/schedule/2011-06-20
    
    :param date: scrape from this date
    
    :return: raw json of schedule of date range
    """
    page_info = {
        "url": 'https://api-web.nhle.com/v1/schedule/{a}'.format(a=date),
        "name": "Schedule_" + date,
        "type": "json_schedule",
        "season": shared.get_season(date),
    }

    return json.loads(shared.get_file(page_info, force=True))


def chunk_schedule_calls(from_date, to_date):
    """
    Due to new API, we have to inividually GET games by week

    We filter out games not in range for the final week
    
    :param date_from: scrape from this date
    :param date_to: scrape until this date

    :return: raw json of schedule of date range
    """
    sched = []
    days_per_call = 7

    from_date = datetime.strptime(from_date, "%Y-%m-%d") 
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    num_days = (to_date - from_date).days + 1  # +1 since difference is looking for total number of days

    for offset in tqdm(range(0, num_days, days_per_call), "Scraping Schedule"):
        date_chunk = datetime.strftime(from_date + timedelta(days=offset), "%Y-%m-%d")
        chunk_sched = get_schedule(date_chunk)['gameWeek']
        sched.append(chunk_sched)

    
    return sched


def scrape_schedule(date_from, date_to, preseason=False, not_over=False):
    """
    Calls getSchedule and scrapes the raw schedule Json

    We filter out games not in range. Due to how new schedule API works
    
    :param date_from: scrape from this date
    :param date_to: scrape until this date
    :param preseason: Boolean indicating whether include preseason games (default if False)
    :param not_over: Boolean indicating whether we scrape games not finished. 
                     Means we relax the requirement of checking if the game is over. 
    
    :return: list with all the game id's
    """
    print("Scraping the schedule between {} and {}...please give it a momment".format(date_from, date_to))

    from_date = datetime.strptime(date_from, "%Y-%m-%d") 
    to_date = datetime.strptime(date_to, "%Y-%m-%d")
    
    schedule = []
    schedule_json = chunk_schedule_calls(date_from, date_to)

    for chunk in schedule_json:
        for day in chunk:
            for game in day['games']:
                game_id = int(str(game['id'])[5:])
                
                # TODO: Confirm if OFF is correct
                status_cond = game['gameState'] == 'OFF' or not_over
                # No preseason or "special" games
                valid_game_cond = (game_id >= 20000 or preseason) and game_id < 40000
                # Within specified date ranges
                game_date = datetime.strptime(game['startTimeUTC'][:10], "%Y-%m-%d")
                date_cond = from_date <= game_date <= to_date

                if status_cond and valid_game_cond and date_cond:
                    schedule.append({
                        "game_id": game['id'], 
                        "date": day['date'], 
                        "start_time": datetime.strptime(game['startTimeUTC'][:-1], "%Y-%m-%dT%H:%M:%S"),
                        "venue": game['venue'].get('default'),
                        "home_team": shared.get_team(game['homeTeam']['abbrev']),
                        "away_team": shared.get_team(game['awayTeam']['abbrev']),
                        "home_score": game['homeTeam'].get("score"),
                        "away_score": game['awayTeam'].get("score"),
                        "status": game["gameState"]
                    })

    return schedule


def get_dates(games):
    """
    Given a list game_ids it returns the dates for each game.

    We sort all the games and retrieve the schedule from the beginning of the season from the earliest game
    until the end of most recent season.
    
    :param games: list with game_id's ex: 2016020001
    
    :return: list with game_id and corresponding date for all games
    """
    today = datetime.today()

    # Determine oldest and newest game
    games = list(map(str, games))
    games.sort()

    date_from = shared.season_start_bound(games[0][:4])
    year_to = int(games[-1][:4])

    # If the last game is part of the ongoing season then only request the schedule until Today
    # We get strange errors if we don't do it like this
    if year_to == shared.get_season(datetime.strftime(today, "%Y-%m-%d")):
        date_to = '-'.join([str(today.year), str(today.month), str(today.day)])
    else:
        date_to = datetime.strftime(shared.season_end_bound(year_to+1), "%Y-%m-%d")  # Newest game in sample

    # TODO: Assume true is live here -> Workaround
    schedule = scrape_schedule(date_from, date_to, preseason=True, not_over=True)

    # Only return games we want in range
    games_list = []
    for game in schedule:
        if str(game['game_id']) in games:
            games_list.extend([game])

    return games_list