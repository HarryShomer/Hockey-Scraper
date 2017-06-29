import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import time


TEAMS = {'ANAHEIM DUCKS': 'ANA', 'ARIZONA COYOTES': 'ARI', 'ATLANTA THRASHERS': 'ATL', 'BOSTON BRUINS': 'BOS',
         'BUFFALO SABRES': 'BUF', 'CAROLINA HURRICANES': 'CAR', 'COLUMBUS BLUE JACKETS': 'CBJ', 'CALGARY FLAMES': 'CGY',
         'CHICAGO BLACKHAWKS': 'CHI', 'COLORADO AVALANCHE': 'COL', 'DALLAS STARS': 'DAL', 'DETROIT RED WINGS': 'DET',
         'EDMONTON OILERS': 'EDM', 'FLORIDA PANTHERS': 'FLA', 'LOS ANGELES KINGS': 'L.A', 'MINNESOTA WILD': 'MIN',
         'MONTREAL CANADIENS': 'MTL',  'CANADIENS MONTREAL': 'MTL', 'NEW JERSEY DEVILS': 'N.J', 'NASHVILLE PREDATORS': 'NSH',
         'NEW YORK ISLANDERS': 'NYI', 'NEW YORK RANGERS': 'NYR', 'OTTAWA SENATORS': 'OTT',  'PHILADELPHIA FLYERS': 'PHI',
         'PHOENIX COYOTES': 'PHX', 'PITTSBURGH PENGUINS': 'PIT', 'SAN JOSE SHARKS': 'S.J',  'ST. LOUIS BLUES': 'STL',
         'TAMPA BAY LIGHTNING': 'T.B', 'TORONTO MAPLE LEAFS': 'TOR', 'VANCOUVER CANUCKS': 'VAN',
         'Vegas Golden Knights': 'VGK', 'WINNIPEG JETS': 'WPG', 'WASHINGTON CAPITALS': 'WSH', }


def analyze_shifts(shift, key, team):
    """
    Analyze shifts for each player when using.
    Prior to this each player (in a dictionary) has a list with each entry being a shift.
    This function is only used for the html
    :param shift: 
    :param key: 
    :param team: 
    :return: 
    """
    shifts = dict()
    shifts['Player'] = key.upper()
    shifts['Period'] = '4' if shift[1] == 'OT' else shift[1]
    shifts['Team'] = TEAMS[team.get_text().strip(' ')]
    shifts['Start'] = convertTime(shift[2].split('/')[0])
    shifts['End'] = convertTime(shift[3].split('/')[0])
    shifts['Duration'] = shifts['End'] - shifts['Start']

    return shifts


def convertTime(minutes):
    """
    Convert from time to just seconds
    :param minutes: minutes elapsed
    :return: time elapsed in seconds
    """
    import datetime
    x = time.strptime(minutes.strip(' '), '%M:%S')

    return datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()


def getSchedule(year):
    """
    Given a year it returns the json for the schedule
    :param year: given year
    :return: raw json of schedule 
    """
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={a}-10-01&endDate={b}-06-20'.format(a=year, b=year+1)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Schedule for {} isn't there".format(year))

    schedule_json = json.loads(response.text)
    time.sleep(1)

    return schedule_json


def getShifts_json(game_id):
    """
    Given a game_id it returns the parsed json
    :param game_id: the game
    :return: DataFrame with info
    """
    url = 'http://www.nhl.com/stats/rest/shiftcharts?cayenneExp=gameId={}'.format(game_id)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Game {} for the shift json isn't there".format(game_id))

    shift_json = json.loads(response.text)
    time.sleep(1)

    return parse_json(shift_json)


def getShifts_html(game_id):
    """
    Given a game_id it returns a DataFrame with the shifts for both teams
    :param game_id: the game
    :return: DataFrame with all shifts
    http://www.nhl.com/scores/htmlreports/20162017/TV020971.HTM
    """
    game_id = str(game_id)
    home_url = 'http://www.nhl.com/scores/htmlreports/{}{}/TH{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])
    away_url = 'http://www.nhl.com/scores/htmlreports/{}{}/TV{}.HTM'.format(game_id[:4], int(game_id[:4])+1, game_id[4:])

    home = requests.get(home_url)
    home.raise_for_status()
    time.sleep(1)

    away = requests.get(away_url)
    away.raise_for_status()
    time.sleep(1)

    away_df=parse_html(away)
    home_df=parse_html(home)

    game_df = pd.concat([away_df, home_df], ignore_index=True)

    game_df = game_df.sort_values(by=['Period', 'Start'], ascending=[True, True])  # Sort by period and by time
    game_df = game_df.reset_index(drop=True)

    return game_df


def parse_shift_json(shift):
    """
    Parse shift for json
    :param shift: 
    :return: dict with shift info
    """
    shift_dict=dict()
    shift_dict['Player'] = ' '.join([shift['firstName'].strip(' ').upper(), shift['lastName'].strip(' ').upper()])
    shift_dict['Period'] = shift['period']
    shift_dict['Team'] = shift['teamAbbrev']
    shift_dict['Start'] = convertTime(shift['startTime'])
    shift_dict['End'] = convertTime(shift['endTime'])
    shift_dict['Duration'] = shift_dict['End'] - shift_dict['Start']

    return shift_dict


def parse_json(json):
    """
    Parse the json
    :param json: raw json
    :return: DataFrame with info
    """
    columns = ['Player', 'Period', 'Team', 'Start', 'End', 'Duration']

    shifts = [parse_shift_json(shift) for shift in json['data']]        # Go through the shifts

    df = pd.DataFrame(shifts, columns=columns)
    df = df.sort_values(by=['Period', 'Start'], ascending=[True, True])  # Sort by period by time
    df = df.reset_index(drop=True)

    return df


def parse_html(html):
    """
    Parse the html
    :param html: raw html
    :return: DataFrame with info
    """

    columns=['Player', 'Period', 'Team', 'Start', 'End', 'Duration']
    df= pd.DataFrame(columns=columns)

    soup = BeautifulSoup(html.content, 'html.parser')
    team = soup.find('td', class_='teamHeading + border')
    td = soup.findAll(True, {'class': ['playerHeading + border', 'lborder + bborder']})

    """
    The list 'td' is laid out with player name followed by every component of each shift. Each shift contains: 
    shift #, Period, begin, end, and duration. The shift event isn't included. 
    """
    players = dict()
    for t in td:
        t=t.get_text()
        if ',' in t:     # If it has a comma in it we know it's a player's name...so add player to dict
            name=t
            # Just format the name normally...it's coded as: 'num# last name, first name'
            name = name.split(',')
            name = ' '.join([name[1].strip(' '), name[0][2:].strip(' ')])
            players[name]=[]
        else:
            # Here we add all the shifts to whatever player we are up to
            players[name].extend([t])

    for key in players.keys():
        # Create a list of lists (each length 5)...corresponds to 5 columns in html shifts
        players[key] = [players[key][i:i + 5] for i in range(0, len(players[key]), 5)]
        shifts = [analyze_shifts(shift, key, team) for shift in players[key]]           # Fix up info
        df = df.append(shifts, ignore_index=True)

    return df


def scrapeSchedule(year):
    """
    Calls getSchedule and scrapes the raw schedule JSON
    :param year: year to scrape
    :return: list with all the game id's
    """
    schedule=[]

    schedule_json=getSchedule(year)
    for date in schedule_json['dates']:
        for game in date['games']:
            schedule.extend([game['gamePk']])

    return schedule


def scrapeGame(game_id):
    """
    Scrape the game.
    Try the json first, if it's not there do the html (it should be there for all games)
    :param game_id: game
    :return: DataFrame with info for the game
    """
    """
    try:
        game_df = getShifts_json(game_id)
        return game_df
    except requests.exceptions.HTTPError:
        try:
            game_df = getShifts_html(game_id)
            return game_df
        except requests.exceptions.HTTPError:
            print("Game {} for shift isn't there".format(game_id))
    """
    game_df = getShifts_html(game_id)
    game_df.to_csv('bar.csv', sep=',')
    return game_df


def scrapeYear(year):
    """
    Calls scrapeSchedule to get the game_id's to scrape and then calls scrapeGame and combines
    all the scraped games into one DataFrame
    :param year: year to scrape
    :return: 
    """
    schedule=scrapeSchedule(year)
    season_df=pd.DataFrame()

    for game in schedule:
        season_df=season_df.append(scrapeGame(game))


"""***Tests***"""
start = time.time()
scrapeGame(2016020971)
end = time.time()
print(end - start)