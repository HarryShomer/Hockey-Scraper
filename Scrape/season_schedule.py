import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import time


def get_schedule(year):
    """
    Given a year it returns the json for the schedule
    :param year: given year
    :return: raw json of schedule 
    """
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}-10-01&endDate={b}-06-20'.format(a=year, b=str(year+1))

    response = requests.Session()
    retries = Retry(total=10, backoff_factor=.1)
    response.mount('http://', HTTPAdapter(max_retries=retries))
    response = response.get(url, timeout=5)
    response.raise_for_status()
    time.sleep(1)

    schedule_json = json.loads(response.text)

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
            schedule.append([game['gamePk'], day['date']])

    return schedule

