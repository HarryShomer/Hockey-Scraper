import json
import time
import hockey_scraper.shared as shared


def get_schedule(date_from, date_to):
    """
   Scrapes games in date range
    Ex: https://statsapi.web.nhl.com/api/v1/schedule?startDate=2010-10-03&endDate=2011-06-20
    :param date_from: scrape from this date
    :param date_to: scrape until this date
    :return: raw json of schedule of date range
    2010-10-03
    """
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}&endDate={b}'.format(a=date_from, b=date_to)

    response = shared.get_url(url)
    time.sleep(1)

    schedule_json = json.loads(response.text)

    return schedule_json


def get_dates(games):
    """
    Given a game_id returns the date of the game
    :param games: ex: 2016020001
    :return: date of game (empty string if can't find it)
    """
    games.sort()

    year_from = str(games[0])[:4]
    year_to = str(games[len(games)-1])[:4]
    date_from = '-'.join([year_from, '10', '1'])             # Earliest games in sample
    date_to = '-'.join([str(int(year_to)+1), '6', '25'])    # Newest game in sample

    schedule = scrape_schedule(date_from, date_to)

    games_list = []
    for game in schedule:
        if game[0] in games:
            games_list.extend([game])

    return games_list


def scrape_schedule(date_from, date_to):
    """
    Calls getSchedule and scrapes the raw schedule JSON
    :param date_from: scrape from this date
    :param date_to: scrape until this date
    :return: list with all the game id's
    """
    schedule = []

    schedule_json = get_schedule(date_from, date_to)
    for day in schedule_json['dates']:
        for game in day['games']:
            # Don't bother with preseason
            if int(str(game['gamePk'])[5:]) >= 20000:
                # schedule[str(game['gamePk'])] = day['date']
                schedule.append([game['gamePk'], day['date']])

    return schedule

