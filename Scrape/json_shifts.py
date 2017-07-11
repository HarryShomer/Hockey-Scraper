import pandas as pd
import requests
import json
import time
import shared_functions


def getShifts_json(game_id):
    """
    Given a game_id it returns the parsed json
    :param game_id: the game
    :return: DataFrame with info
    """
    url = 'http://www.nhl.com/stats/rest/shiftcharts?cayenneExp=gameId={}'.format(game_id)

    response = requests.get(url)
    response.raise_for_status()

    shift_json = json.loads(response.text)
    time.sleep(1)

    try:
        df = parse_json(shift_json)
    except Exception:
        print('Problem with the shift reports for game {}'.format(game_id))
        return None

    return df


def parse_shift_json(shift):
    """
    Parse shift for json
    :param shift: 
    :return: dict with shift info
    """
    shift_dict = dict()
    shift_dict['Player'] = ' '.join([shift['firstName'].strip(' ').upper(), shift['lastName'].strip(' ').upper()])
    shift_dict['Player_Id'] = shift['playerId']
    shift_dict['Period'] = shift['period']
    shift_dict['Team'] = shift['teamAbbrev']
    shift_dict['Start'] = shared_functions.convert_to_seconds(shift['startTime'])
    shift_dict['End'] = shared_functions.convert_to_seconds(shift['endTime'])
    shift_dict['Duration'] = shift['duration']

    return shift_dict


def parse_json(json):
    """
    Parse the json
    :param json: raw json
    :return: DataFrame with info
    """
    columns = ['Player', 'Player_Id', 'Period', 'Team', 'Start', 'End', 'Duration']

    shifts = [parse_shift_json(shift) for shift in json['data']]       # Go through the shifts

    df = pd.DataFrame(shifts, columns=columns)
    df = df.sort_values(by=['Period', 'Start'], ascending=[True, True])  # Sort by period by time
    df = df.reset_index(drop=True)

    return df


def scrapeGame(game_id):
    """
    Scrape the game.
    Try the json first, if it's not there do the html (it should be there for all games)
    :param game_id: game
    :return: DataFrame with info for the game
    """
    game_df = getShifts_json(game_id)

    return game_df



