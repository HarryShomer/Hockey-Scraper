"""
This file is a bunch of the shared functions or just general stuff used by the different scrapers in the package.
"""
import os
import time
import json
import logging
import warnings
import requests
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from . import save_pages as sp
from . import config
import inspect

# Directory where this file lives
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

# Name and Team fixes used 
with open(os.path.join(FILE_DIR, "player_name_fixes.json"), "r" ,encoding="utf-8") as f:
    Names = json.load(f)['fixes']

with open(os.path.join(FILE_DIR, "team_tri_codes.json"), "r" ,encoding="utf-8") as f:
    TEAMS = json.load(f)['teams']

with open(os.path.join(FILE_DIR, "tri_code_conversion.json"), "r" ,encoding="utf-8") as f:
    TRI_CODES = json.load(f)['tri_codes']


def fix_name(name):
    """
    Check if a name falls under those that need fixing. If it does...fix it.

    :param name: name in pbp

    :return: Either the given parameter or the fixed name
    """
    return Names.get(name.upper(), name.upper()).upper()


def get_team(team):
    """
    Get the fucking team
    """
    return TEAMS.get(team.upper(), team.upper()).upper()


def convert_tricode(tri):
    """
    Convert the tri-code if found in 'tri_code_conversion.json'

    :return Fixed tri-code or original
    """
    return TRI_CODES.get(tri.upper(), tri.upper()).upper()


def custom_formatwarning(msg, *args, **kwargs): 
    """
    Override format for standard wanings
    """
    ansi_no_color = '\033[0m'
    return "{msg}\n{no_color}".format(no_color=ansi_no_color, msg=msg)
    
warnings.formatwarning = custom_formatwarning


def print_error(msg):
    """
    Implement own custom error using warning module. Prints in red

    Reason why i still use warning for errors is so i can set to ignore them if i want to (e.g. live_scrape line 200).

    :param msg: Str to print

    :return: None
    """
    ansi_red_code = '\033[0;31m'
    warning_msg = "{}Error: {}".format(ansi_red_code, msg)

    # if config.LOG:
    #     caller_file = os.path.basename(inspect.stack()[1].filename)
    #     get_logger(caller_file).error(msg + " " + verbose)

    warnings.warn(warning_msg) 


def print_warning(msg):
    """
    Implement own custom warning using warning module. Prints in Orange.

    :param msg: Str to print

    :return: None
    """
    ansi_yellow_code = '\033[0;33m'
    warning_msg = "{}Warning: {}".format(ansi_yellow_code, msg)

    warnings.warn(warning_msg)


def get_logger(python_file):
    """
    Create a basic logger to a log file

    :param python_file: File that instantiates the logger instance
    
    :return: logger 
    """
    base_py_file = os.path.basename(python_file)

    # If already exists we don't try to recreate it
    if base_py_file in logging.Logger.manager.loggerDict.keys():
        return logging.getLogger(base_py_file)

    logger = logging.getLogger(base_py_file)
    logger.setLevel(logging.INFO)  
    
    fh = logging.FileHandler("hockey_scraper_errors_{}.log".format(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))) 
    fh.setFormatter(logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %I:%M:%S'))
    logger.addHandler(fh)

    return logger


def log_error(err, py_file):
    """
    Log error when Logging is specified

    :param err: Error to log
    :param python_file: File that instantiates the logger instance

    :return: None
    """
    if config.LOG:
        get_logger(py_file).error(err)


def get_season(date):
    """
    Get Season based on from_date

    There is an exception for the 2019-2020 pandemic season. Accoding to the below url:
        -  2019-2020 season ends in Oct. 2020
        -  2020-2021 season begins in November 2020
        -  https://nhl.nbcsports.com/2020/07/10/new-nhl-critical-dates-calendar-means-an-october-free-agent-frenzy/

    :param date: date

    :return: season -> ex: 2016 for 2016-2017 season
    """
    year = date[:4]
    date = datetime.strptime(date, "%Y-%m-%d")
    initial_bound = datetime.strptime('-'.join([year, '01-01']), "%Y-%m-%d")

    # End bound for year1-year2 season is later for pandemic year
    if initial_bound <= date <= season_end_bound(year):
        return int(year) - 1

    return int(year)


def season_start_bound(year):
    """
    Get start bound for a season.

    Notes:
     - There is a bug in the schedule API for 2016 that causes the pushback to 09-30
     - Pandemic season started in January

    :param year: str of year for given date

    :return: str of first date in season
    """
    if int(year) == 2016:
        return "2016-09-30"
        
    if int(year) == 2020:
        return '2021-01-01'

    return "{}-09-01".format(str(year))



def season_end_bound(year):
    """
    Determine the end bound of a given season. Changes depending on if it's the pandemic season or not

    :param year: str of year for given date

    :return: Datetime obj of last date in season
    """
    normal_end_bound = datetime.strptime('-'.join([str(year), '08-31']), "%Y-%m-%d")
    pandemic_end_bound = datetime.strptime('-'.join([str(year), '10-31']), "%Y-%m-%d")

    if int(year) == 2020:
        return pandemic_end_bound

    return normal_end_bound


def convert_to_seconds(minutes):
    """
    Return minutes elapsed in time format to seconds elapsed

    :param minutes: time elapsed

    :return: time elapsed in seconds
    """
    if minutes == '-16:0-':
        return '1200'      # Sometimes in the html at the end of the game the time is -16:0-

    # If the time is junk not much i can do
    try:
        x = time.strptime(minutes.strip(' '), '%M:%S')
    except ValueError:
        return None

    return timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()


def if_rescrape(user_rescrape):
    """
    If you want to re_scrape. If someone is a dumbass and feeds it a non-boolean it terminates the program

    Note: Only matters when you have a directory specified

    :param user_rescrape: Boolean

    :return: None
    """
    if isinstance(user_rescrape, bool):
        config.RESCRAPE = user_rescrape
    else:
        raise ValueError("Error: 'if_rescrape' must be a boolean. Not a {}".format(type(user_rescrape)))


def add_dir(user_dir):
    """
    Add directory to store scraped docs if valid. Or create in the home dir

    NOTE: After this functions docs_dir is either None or a valid directory

    :param user_dir: If bool=True create in the home dire or if user provided directory on their machine

    :return: None
    """
    # False so they don't want it
    if not user_dir:
        config.DOCS_DIR = False
        return

    # Something was given
    # Either True or string to directory
    # If boolean refer to the home directory
    if isinstance(user_dir, bool):
        config.DOCS_DIR = os.path.join(os.path.expanduser('~'), "hockey_scraper_data")
        # Create if needed
        if not os.path.isdir(config.DOCS_DIR):
            print_warning("Creating the hockey_scraper_data directory in the home directory")
            os.mkdir(config.DOCS_DIR)
    elif isinstance(user_dir, str) and os.path.isdir(user_dir):
        config.DOCS_DIR = user_dir
    elif not (isinstance(user_dir, str) and isinstance(user_dir, bool)):
        config.DOCS_DIR = False
        print_error("The docs_dir argument provided is invalid")
    else:
        config.DOCS_DIR = False
        print_error("The directory specified for the saving of scraped docs doesn't exist. Therefore:"
              "\n1. All specified games will be scraped from their appropriate sources (NHL or ESPN)."
              "\n2. All scraped files will NOT be saved at all. Please either create the directory you want them to be "
              "deposited in or recheck the directory you typed in and start again.\n")


def scrape_page(url):
    """
    Scrape a given url

    :param url: url for page

    :return: response object
    """
    response = requests.Session()
    retries = Retry(total=10, backoff_factor=.1)
    response.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        response = response.get(url, timeout=5)
        response.raise_for_status()
        page = response.text
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        page = None
    except requests.exceptions.ReadTimeout:
        # If it times out and it's the schedule print an error message...otherwise just make the page = None
        if "schedule" in url:
            raise Exception("Timeout Error: The NHL API took too long to respond to our request. "
                                "Please Try Again (you may need to try a few times before it works). ")
        else:
            print_error("Timeout Error: The server took too long to respond to our request.")
            page = None

    # Pause for 1 second - make it more if you want
    time.sleep(1)

    return page



def get_file(file_info, force=False):
    """
    Get the specified file.

    If a docs_dir is provided we check if it exists. If it does we see if it contains that page (and saves if it
    doesn't). If the docs_dir doesn't exist we just scrape from the source and not save.

    :param file_info: Dictionary containing the info for the file.
                      Contains the url, name, type, and season
    :param force: Force a rescrape. Default is False

    :return: page
    """
    file_info['dir'] = config.DOCS_DIR

    # If everything checks out we'll retrieve it, otherwise we scrape it
    if file_info['dir'] and sp.check_file_exists(file_info) and not config.RESCRAPE and not force:
        page = sp.get_page(file_info)
    else:
        page = scrape_page(file_info['url'])
        sp.save_page(page, file_info)

    return page


def check_data_format(data_format):
    """
    Checks if data_format specified (if it is at all) is either None, 'Csv', or 'pandas'.
    It exits program with error message if input isn't good.

    :param data_format: data_format provided 

    :return: Boolean - True if good
    """
    if not data_format or data_format.lower() not in ['csv', 'pandas']:
        raise ValueError('{} is an unspecified data format. The two options are Csv and Pandas '
                            '(Csv is default)\n'.format(data_format))


def check_valid_dates(from_date, to_date):
    """
    Check if it's a valid date range

    :param from_date: date should scrape from
    :param to_date: date should scrape to

    :return: None
    """
    try:
        if time.strptime(to_date, "%Y-%m-%d") < time.strptime(from_date, "%Y-%m-%d"):
            raise ValueError("Error: The second date input is earlier than the first one")
    except ValueError:
        raise ValueError("Error: Incorrect format given for dates. They must be given like 'yyyy-mm-dd' "
                            "(ex: '2016-10-01').")


def to_csv(base_file_name, df, league, file_type):
    """
    Write DataFrame to csv file

    :param base_file_name: name of file
    :param df: DataFrame
    :param league: nhl or nwhl
    :param file_type: type of file despoiting

    :return: None
    """
    docs_dir = config.DOCS_DIR

    # This was a late addition so we add support here
    if isinstance(docs_dir, str) and not os.path.isdir(os.path.join(docs_dir, "csvs")):
        os.mkdir(os.path.join(docs_dir, "csvs"))

    if df is not None:
        if isinstance(docs_dir, str):
            file_name = os.path.join(docs_dir, "csvs", '{}_{}_{}.csv'.format(league, file_type, base_file_name))
        else:
            file_name = '{}_{}_{}.csv'.format(league, file_type, base_file_name)

        print("---> {} {} data deposited in file - {}".format(league, file_type, file_name))
        df.to_csv(file_name, sep=',', encoding='utf-8')

