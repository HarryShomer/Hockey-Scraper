"""
This module contains functions to scrape the Json toi/shifts for any given game
"""

import json
import pandas as pd
import hockey_scraper.utils.shared as shared


def get_shifts(game_id):
    """
    Given a game_id it returns the raw json
    Ex: https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId=2019020001
    
    :param game_id: the game
    
    :return: json or None
    """
    page_info = {
        "url": 'https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={}'.format(game_id),
        "name": str(game_id),
        "type": "json_shifts",
        "season": str(game_id)[:4],
    }

    response = shared.get_file(page_info)

    # Return empty dict if can't get page
    if not response:
        return {}
    else:
        return json.loads(response)


def fix_team_tricode(tricode):
    """
    Some of the tricodes are different than how I want them
    
    :param tricode: 3 letter team name - ex: NYR
    
    :return: fixed tricode
    """
    fixed_tricodes = {
        'TBL':  'T.B',
        'LAK': 'L.A',
        'NJD': 'N.J',
        'SJS': 'S.J'
    }

    return fixed_tricodes.get(tricode.upper(), tricode)


def parse_shift(shift):
    """
    Parse shift for json
    
    :param shift: json for shift
    
    :return: dict with shift info
    """
    shift_dict = dict()

    # At the end of the json they list when all the goal events happened. We don't want them...
    # They are the only one's which have their eventDescription be not null
    if shift['eventDescription'] is not None:
        return {}

    name = shared.fix_name(' '.join([shift['firstName'].strip(' '), shift['lastName'].strip(' ')]))
    
    shift_dict['Player'] = name
    shift_dict['Player_Id'] = shift['playerId']
    shift_dict['Period'] = shift['period']
    shift_dict['Team'] = fix_team_tricode(shift['teamAbbrev'])
    shift_dict['Start'] = shared.convert_to_seconds(shift['startTime'])
    shift_dict['End'] = shared.convert_to_seconds(shift['endTime'])
    shift_dict['Duration'] = shared.convert_to_seconds(shift['duration'])


    return shift_dict


def parse_json(shift_json, game_id):
    """
    Parse the json
    
    :param shift_json: raw json
    :param game_id: if of game
    
    :return: DataFrame with info
    """
    columns = ['Game_Id', 'Period', 'Team', 'Player', 'Player_Id', 'Start', 'End', 'Duration']

    shifts = [parse_shift(shift) for shift in shift_json['data']]  # Go through the shifts
    shifts = [shift for shift in shifts if shift != {}]            # Get rid of null shifts (which happen at end)

    df = pd.DataFrame(shifts, columns=columns)
    df['Game_Id'] = str(game_id)[5:]
    df = df.sort_values(by=['Period', 'Start'], ascending=[True, True])  

    return df.reset_index(drop=True)


def scrape_game(game_id):
    """
    Scrape the game. 
    
    :param game_id: game
    
    :return: DataFrame with info for the game
    """
    shifts_json = get_shifts(game_id)

    if not shifts_json:
        #shared.print_error("Json shifts for game {} is either not there or can't be obtained".format(game_id))
        return pd.DataFrame()

    try:
        game_df = parse_json(shifts_json, game_id)
    except Exception as e:
        shared.print_error('Error parsing Json shifts for game {} {}'.format(game_id, e))
        return pd.DataFrame()

    return game_df

