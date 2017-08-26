from collections import namedtuple

from scrape import shared


ScheduleGame = namedtuple('ScheduleGame', 'id date')


def get_schedule(year):
    """
    Given a year it returns the json for the schedule
    Ex: https://statsapi.web.nhl.com/api/v1/schedule?startDate=2010-10-03&endDate=2011-06-20

    :param year: given year
    :return: raw json of schedule
    """
    response = shared.get_url(
        'https://statsapi.web.nhl.com/api/v1/schedule',
        params={
            'startDate': '{}-10-01'.format(year),
            'endDate': '{}-06-20'.format(year + 1),
        }
    )

    return response.json()


def scrape_schedule(year):
    """
    Scrape the raw schedule JSON

    :param year: year to scrape
    :returns: list of (game ID, date) pairs
    """
    schedule = get_schedule(year)

    return [ScheduleGame(game['gamePk'], day['date'])
            for day in schedule['dates']
            for game in day['games']]
