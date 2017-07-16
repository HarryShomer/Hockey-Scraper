import requests
import json
import time


def get_schedule(year):
    """
    Given a year it returns the json for the schedule
    :param year: given year
    :return: raw json of schedule 
    """
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}-10-01&endDate={b}-06-20'.format(a=year, b=year+1)

    response = requests.get(url)
    response.raise_for_status()

    schedule_json = json.loads(response.text)
    time.sleep(1)

    return schedule_json


def scrape_schedule(year):
    """
    Calls getSchedule and scrapes the raw schedule JSON
    :param year: year to scrape
    :return: list with all the game id's
    """
    schedule=[]

    schedule_json=get_schedule(year)
    for day in schedule_json['dates']:
        for game in day['games']:
            schedule.extend([game['gamePk'], day['date']])

    return schedule

