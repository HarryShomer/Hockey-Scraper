import pandas as pd
import json
import time
import shared


def get_shifts(game_id):
    """
    Given a game_id it returns the raw json
    Ex: http://www.nhl.com/stats/rest/shiftcharts?cayenneExp=gameId=2010020001
    :param game_id: the game
    :return: 
    """
    url = 'http://www.nhl.com/stats/rest/shiftcharts?cayenneExp=gameId={}'.format(game_id)
    response = shared.get_url(url)
    time.sleep(1)

    shift_json = json.loads(response.text)
    return parse_json(shift_json, game_id)


def parse_shift(shift):
    """
    Parse shift for json
    :param shift: json for shift
    :return: dict with shift info
    """
    shift_dict = dict()
    name = shared.fix_name(' '.join([shift['firstName'].strip(' ').upper(), shift['lastName'].strip(' ').upper()]))
    shift_dict['Player'] = name
    shift_dict['Player_Id'] = shift['playerId']
    shift_dict['Period'] = shift['period']
    shift_dict['Team'] = shift['teamAbbrev']

    # At the end of the json they list when all the goal events happened. They are the only one's which have their
    # eventDescription be not null
    if shift['eventDescription'] is None:
        shift_dict['Start'] = shared.convert_to_seconds(shift['startTime'])
        shift_dict['End'] = shared.convert_to_seconds(shift['endTime'])
        shift_dict['Duration'] = shared.convert_to_seconds(shift['duration'])
    else:
        shift_dict = dict()

    return shift_dict


def parse_json(shift_json, game_id):
    """
    Parse the json
    :param shift_json: raw json
    :param game_id: if of game
    :return: DataFrame with info
    """
    columns = ['Game_Id', 'Period', 'Team', 'Player', 'Player_Id', 'Start', 'End', 'Duration']

    shifts = [parse_shift(shift) for shift in shift_json['data']]     # Go through the shifts
    shifts = [shift for shift in shifts if shift != {}]               # Get rid of null shifts (which happen at end)

    df = pd.DataFrame(shifts, columns=columns)
    df['Game_Id'] = str(game_id)
    df = df.sort_values(by=['Period', 'Start'], ascending=[True, True])  # Sort by period by time
    df = df.reset_index(drop=True)

    return df


def scrape_game(game_id):
    """
    Scrape the game.
    Try the json first, if it's not there do the html (it should be there for all games)
    :param game_id: game
    :return: DataFrame with info for the game
    """
    game_df = get_shifts(game_id)

    return game_df



