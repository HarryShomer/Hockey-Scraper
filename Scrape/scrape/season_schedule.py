import json
import time

from scrape import shared


def get_schedule(year):
    """
    Given a year it returns the json for the schedule
    Ex: https://statsapi.web.nhl.com/api/v1/schedule?startDate=2010-10-03&endDate=2011-06-20
    :param year: given year
    :return: raw json of schedule
    """
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}-10-01&endDate={b}-06-20'.format(a=year, b=str(year+1))

    response = shared.get_url(url)
    time.sleep(1)

    schedule_json = json.loads(response.text)

    return schedule_json


def scrape_schedule(year):
    """
    Calls getSchedule and scrapes the raw schedule JSON
    :param year: year to scrape
    :return: list with all the game id's
    """
    schedule = []

    schedule_json = get_schedule(year)
    for day in schedule_json['dates']:
        for game in day['games']:
            schedule.append([game['gamePk'], day['date']])

    return schedule
