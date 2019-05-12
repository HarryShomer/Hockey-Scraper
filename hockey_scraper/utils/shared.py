#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is a bunch of the shared functions or just general stuff used by the different scrapers in the package.
"""

import os
import time
import warnings
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from . import save_pages as sp


# Own warning...gets rid of junk when printing
def custom_formatwarning(msg, *args, **kwargs): return "Warning: " + str(msg) + '\n'
warnings.formatwarning = custom_formatwarning

# Directory where to save pages
docs_dir = False

# Boolean that tells us whether or not we should re-scrape a given page if it's already saved
re_scrape = False

# All the corresponding tri-codes for team names
TEAMS = {
    'ANAHEIM DUCKS': 'ANA', 'ARIZONA COYOTES': 'ARI', 'ATLANTA THRASHERS': 'ATL', 'BOSTON BRUINS': 'BOS',
    'BUFFALO SABRES': 'BUF', 'CAROLINA HURRICANES': 'CAR', 'COLUMBUS BLUE JACKETS': 'CBJ', 'CALGARY FLAMES': 'CGY',
    'CHICAGO BLACKHAWKS': 'CHI', 'COLORADO AVALANCHE': 'COL', 'DALLAS STARS': 'DAL', 'DETROIT RED WINGS': 'DET',
    'EDMONTON OILERS': 'EDM', 'FLORIDA PANTHERS': 'FLA', 'LOS ANGELES KINGS': 'L.A', 'MINNESOTA WILD': 'MIN',
    'MONTREAL CANADIENS': 'MTL', u'MONTRÉAL CANADIENS': 'MTL', 'CANADIENS MONTREAL': 'MTL', 'NEW JERSEY DEVILS': 'N.J',
    'NASHVILLE PREDATORS': 'NSH', 'NEW YORK ISLANDERS': 'NYI', 'NEW YORK RANGERS': 'NYR', 'OTTAWA SENATORS': 'OTT',
    'PHILADELPHIA FLYERS': 'PHI', 'PHOENIX COYOTES': 'PHX', 'PITTSBURGH PENGUINS': 'PIT', 'SAN JOSE SHARKS': 'S.J',
    'ST. LOUIS BLUES': 'STL', 'TAMPA BAY LIGHTNING': 'T.B', 'TORONTO MAPLE LEAFS': 'TOR', 'VANCOUVER CANUCKS': 'VAN',
    'VEGAS GOLDEN KNIGHTS': 'VGK', 'WINNIPEG JETS': 'WPG', 'WASHINGTON CAPITALS': 'WSH', 'BERN SC BERN': 'BSB',
    'KOLN HAIE': "KHI"
}


# Fixes some of the mistakes made with player names
# A majority of this is courtesy of Muneeb Alam (on twitter: @muneebalamcu)
# Found here -> https://github.com/muneebalam/Hockey/blob/master/NHL/Core/GetPbP.py
Names = {'n/a': 'n/a', 'ALEXANDER OVECHKIN': 'Alex Ovechkin', 'TOBY ENSTROM': 'Tobias Enstrom', 'JAMIE MCGINN': 'Jamie McGinn',
         'CODY MCLEOD': 'Cody McLeod', 'MARC-EDOUARD VLASIC': 'Marc-Edouard Vlasic', 'RYAN MCDONAGH': 'Ryan McDonagh',
         'CHRIS TANEV': 'Christopher Tanev', 'JARED MCCANN': 'Jared McCann', 'P.K. SUBBAN': 'PK Subban',
         'DEVANTE SMITH-PELLY': 'Devante Smith-Pelly', 'MIKE MCKENNA': 'Mike McKenna', 'MICHAEL MCCARRON': 'Michael McCarron',
         'T.J. BRENNAN': 'TJ Brennan', 'BRAYDEN MCNABB': 'Brayden McNabb', 'PIERRE-ALEXANDRE PARENTEAU': 'PA Parenteau',
         'JAMES VAN RIEMSDYK': 'James van Riemsdyk', 'OLIVER EKMAN-LARSSON': 'Oliver Ekman-Larsson', 'TJ OSHIE': 'TJ Oshie',
         'J P DUMONT': 'JP Dumont', 'J.T. MILLER': 'JT Miller', 'R.J UMBERGER': 'RJ Umberger', 'PA PARENTEAU': 'PA Parenteau',
         'PER-JOHAN AXELSSON': 'P.J. Axelsson', 'MAXIME TALBOT': 'Max Talbot', 'JOHN-MICHAEL LILES': 'John-Michael Liles',
         'DANIEL GIRARDI': 'Dan Girardi', 'DANIEL CLEARY': 'Dan Cleary', 'NIKLAS KRONVALL': 'Niklas Kronwall',
         'SIARHEI KASTSITSYN': 'Sergei Kostitsyn', 'ANDREI KASTSITSYN': 'Andrei Kostitsyn', 'ALEXEI KOVALEV': 'Alex Kovalev',
         'DAVID JOHNNY ODUYA': 'Johnny Oduya', 'EDWARD PURCELL': 'Teddy Purcell', 'NICKLAS GROSSMAN': 'Nicklas Grossmann',
         'PERNELL KARL SUBBAN': 'PK Subban', 'VOJTEK VOLSKI': 'Wojtek Wolski', 'VYACHESLAV VOYNOV': 'Slava Voynov',
         'FREDDY MODIN': 'Fredrik Modin', 'VACLAV PROSPAL': 'Vinny Prospal', 'KRISTOPHER LETANG': 'Kris Letang',
         'PIERRE ALEXANDRE PARENTEAU': 'PA Parenteau', 'T.J. OSHIE': 'TJ Oshie', 'JOHN HILLEN III': 'Jack Hillen',
         'BRANDON CROMBEEN': 'B.J. Crombeen', 'JEAN-PIERRE DUMONT': 'JP Dumont', 'RYAN NUGENT-HOPKINS': 'Ryan Nugent-Hopkins',
         'CONNOR MCDAVID': 'Connor McDavid', 'TREVOR VAN RIEMSDYK': 'Trevor van Riemsdyk', 'CALVIN DE HAAN': 'Calvin de Haan',
         'GREG MCKEGG': 'Greg McKegg', 'NATHAN MACKINNON': 'Nathan MacKinnon', 'KYLE MCLAREN': 'Kyle McLaren',
         'ADAM MCQUAID': 'Adam McQuaid', 'DYLAN MCILRATH': 'Dylan McIlrath', 'DANNY DEKEYSER': 'Danny DeKeyser',
         'JAKE MCCABE': 'Jake McCabe', 'JAMIE MCBAIN': 'Jamie McBain', 'PIERRE-MARC BOUCHARD': 'Pierre-Marc Bouchard',
         'JEAN-FRANCOIS JACQUES': 'JF Jacques', 'OLE-KRISTIAN TOLLEFSEN': 'Ole-Kristian Tollefsen',
         'MARC-ANDRE BERGERON': 'Marc-Andre Bergeron', 'MARC-ANTOINE POULIOT': 'Marc-Antoine Pouliot',
         'MARC-ANDRE GRAGNANI': 'Marc-Andre Gragnani', 'JORDAN LAVALLEE-SMOTHERMAN': 'Jordan Lavallee-Smotherman',
         'PIERRE-LUC LETOURNEAU-LEBLOND': 'Pierre Leblond', 'J-F JACQUES': 'JF Jacques', 'JP DUMONT': 'JP Dumont',
         'MARC-ANDRE CLICHE': 'Marc-Andre Cliche', 'J-P DUMONT': 'JP Dumont', 'JOSHUA BAILEY': 'Josh Bailey',
         'OLIVIER MAGNAN-GRENIER': 'Olivier Magnan-Grenier', u'FRÉDÉRIC ST-DENIS': 'Frederic St-Denis',
         'MARC-ANDRE BOURDON': 'Marc-Andre Bourdon', 'PIERRE-CEDRIC LABRIE': 'Pierre-Cedric Labrie',
         'JONATHAN AUDY-MARCHESSAULT': 'Jonathan Marchessault', 'JEAN-GABRIEL PAGEAU': 'Jean-Gabriel Pageau',
         'JEAN-PHILIPPE COTE': 'Jean-Philippe Cote', 'PIERRE-EDOUARD BELLEMARE': 'Pierre-Edouard Bellemare',
         'COLIN (JOHN) WHITE': 'Colin White', 'BATES (JON) BATTAGLIA': 'Bates Battaglia', 'MATHEW DUBMA': 'Matt Dumba',
         'NIKOLAI ANTROPOV': 'Nik Antropov', 'KRYS BARCH': 'Krystofer Barch', 'CAMERON BARKER': 'Cam Barker',
         'NICKLAS BERGFORS': 'Niclas Bergfors', 'ROBERT BLAKE': 'Rob Blake', 'MICHAEL BLUNDEN': 'Mike Blunden',
         'CHRISTOPHER BOURQUE': 'Chris Bourque', 'MICHÃ«L BOURNIVAL': 'Michael Bournival', 'NICHOLAS BOYNTON': 'Nick Boynton',
         'TJ BRENNAN': 'TJ Brennan', 'DANIEL BRIERE': 'Danny Briere', 'TJ BRODIE': 'TJ Brodie', 'J.T. BROWN': 'JT Brown',
         'ALEXANDRE BURROWS': 'Alex Burrows', 'MICHAEL CAMMALLERI': 'Mike Cammalleri', 'DANIEL CARCILLO': 'Dan Carcillo',
         'MATTHEW CARLE': 'Matt Carle', 'DANNY CLEARY': 'Dan Cleary', 'JOSEPH CORVO': 'Joe Corvo', 'JOSEPH CRABB': 'Joey Crabb',
         'BJ CROMBEEN': 'B.J. Crombeen',  'EVGENII DADONOV': 'Evgeny Dadonov', 'CHRIS VANDE VELDE': 'Chris VandeVelde',
         'JACOB DE LA ROSE': 'Jacob de la Rose', 'JOE DIPENTA': 'Joe DiPenta', 'JON DISALVATORE': 'Jon DiSalvatore',
         'JACOB DOWELL': 'Jake Dowell', 'NICHOLAS DRAZENOVIC': 'Nick Drazenovic', 'ROBERT EARL': 'Robbie Earl',
         'ALEXANDER FROLOV': 'Alex Frolov', 'T.J. GALIARDI': 'TJ Galiardi', 'TJ GALIARDI': 'TJ Galiardi',
         'ANDREW GREENE': 'Andy Greene', 'MICHAEL GRIER': 'Mike Grier', 'NATHAN GUENIN': 'Nate Guenin',
         'MARTY HAVLAT': 'Martin Havlat', 'JOSHUA HENNESSY': 'Josh Hennessy', 'T.J. HENSICK': 'TJ Hensick',
         'TJ Hensick': 'TJ Hensick', 'CHRISTOPHER HIGGINS': 'Chris Higgins', 'ROBERT HOLIK': 'Bobby Holik',
         'MATTHEW IRWIN': 'Matt Irwin', 'P. J. AXELSSON': 'P.J. Axelsson', 'PER JOHAN AXELSSON': 'P.J. Axelsson',
         'JONATHON KALINSKI': 'Jon Kalinski', 'ALEXANDER KHOKHLACHEV': 'Alex Khokhlachev', 'DJ KING': 'DJ King',
         'DWAYNE KING': 'DJ King', 'MICHAEL KNUBLE': 'Mike Knuble', 'KRYSTOFER KOLANOS': 'Krys Kolanos',
         'MICHAEL KOMISAREK': 'Mike Komisarek', 'STAFFAN KRONVALL': 'Staffan Kronwall', 'NIKOLAY KULEMIN': 'Nikolai Kulemin',
         'CLARKE MACARTHUR': 'Clarke MacArthur', 'LANE MACDERMID': 'Lane MacDermid', 'ANDREW MACDONALD': 'Andrew MacDonald',
         'RAYMOND MACIAS': 'Ray Macias', 'CRAIG MACDONALD': 'Craig MacDonald', 'STEVE MACINTYRE': 'Steve MacIntyre',
         'MAKSIM MAYOROV': 'Maxim Mayorov', 'AARON MACKENZIE': 'Aaron MacKenzie', 'DEREK MACKENZIE': 'Derek MacKenzie',
         'RODNEY PELLEY': 'Rod Pelley', 'BRETT MACLEAN': 'Brett MacLean', 'ANDREW MACWILLIAM': 'Andrew MacWilliam',
         'BRYAN MCCABE': 'Bryan McCabe', 'OLIVIER MAGNAN': 'Olivier Magnan-Grenier', 'DEAN MCAMMOND': 'Dean McAmmond',
         'KENNDAL MCARDLE': 'Kenndal McArdle', 'ANDY MCDONALD': 'Andy McDonald', 'COLIN MCDONALD': 'Colin McDonald',
         'JOHN MCCARTHY': 'John McCarthy', 'STEVE MCCARTHY': 'Steve McCarthy', 'DARREN MCCARTY': 'Darren McCarty',
         'JAY MCCLEMENT': 'Jay McClement', 'CODY MCCORMICK': 'Cody McCormick', 'MAX MCCORMICK': 'Max McCormick',
         'BROCK MCGINN': 'Brock McGinn', 'TYE MCGINN': 'Tye McGinn', 'BRIAN MCGRATTAN': 'Brian McGrattan',
         'DAVID MCINTYRE': 'David McIntyre', 'NATHAN MCIVER': 'Nathan McIver', 'JAY MCKEE': 'Jay McKee',
         'CURTIS MCKENZIE': 'Curtis McKenzie', 'FRAZER MCLAREN': 'Frazer McLaren', 'BRETT MCLEAN': 'Brett McLean',
         'BRANDON MCMILLAN': 'Brandon McMillan', 'CARSON MCMILLAN': 'Carson McMillan', 'PHILIP MCRAE':
         'Philip McRae', 'FREDERICK MEYER IV': 'Freddy Meyer', 'MICHAEL MODANO': 'Mike Modano',
         'CHRISTOPHER NEIL': 'Chris Neil', 'MATTHEW NIETO': 'Matt Nieto', 'JOHN ODUYA': 'Johnny Oduya',
         'PIERRE PARENTEAU': 'PA Parenteau', 'MARC POULIOT': 'Marc-Antoine Pouliot', 'MAXWELL REINHART': 'Max Reinhart',
         'MICHAEL RUPP': 'Mike Rupp', 'ROBERT SCUDERI': 'Rob Scuderi', 'TOMMY SESTITO': 'Tom Sestito',
         'MICHAEL SILLINGER': 'Mike Sillinger', 'JONATHAN SIM': 'Jon Sim', 'MARTIN ST LOUIS': 'Martin St. Louis',
         'MATTHEW STAJAN': 'Matt Stajan', 'ZACHERY STORTINI': 'Zack Stortini', 'PK SUBBAN': 'PK Subban',
         'WILLIAM THOMAS': 'Bill Thomas', 'R.J. UMBERGER': 'RJ Umberger', 'RJ UMBERGER': 'RJ Umberger',
         'MARK VAN GUILDER': 'Mark van Guilder', 'BRYCE VAN BRABANT': 'Bryce van Brabant',
         'DAVID VAN DER GULIK': 'David van der Gulik', 'MIKE VAN RYN': 'Mike van Ryn', 'ANDREW WOZNIEWSKI': 'Andy Wozniewski',
         'JAMES WYMAN': 'JT Wyman', 'JT WYMAN': 'JT Wyman', 'NIKOLAY ZHERDEV': 'Nikolai Zherdev',
         'HARRISON ZOLNIERCZYK': 'Harry Zolnierczyk', 'MARTIN ST PIERRE': 'Martin St. Pierre', 'B.J CROMBEEN': 'B.J. Crombeen',
         'DENIS GAUTHIER JR.': 'DENIS GAUTHIER', 'DENIS JR. GAUTHIER': 'DENIS GAUTHIER', 'MARC-ANDRE FLEURY': 'Marc-Andre Fleury',
         'DAN LACOUTURE': 'Dan LaCouture', 'RICK DIPIETRO': 'Rick DiPietro', 'JOEY MACDONALD': 'Joey MacDonald',
         'TIMOTHY JR. THOMAS': 'Tim Thomas', 'ILJA BRYZGALOV': 'Ilya Bryzgalov', 'MATHEW DUMBA': 'Matt Dumba',
         'MICHAËL BOURNIVAL': 'Michael Bournival', 'MATTHEW BENNING': 'Matt Benning', 'ZACHARY SANFORD': 'Zach Sanford',
         'AJ GREER': 'A.J. Greer', 'JT COMPHER': 'J.T. Compher', 'NICOLAS PETAN': 'Nic Petan',
         'VINCENT HINOSTROZA': 'Vinnie Hinostroza', 'PHILIP VARONE': 'Phil Varone', 'JOSHUA MORRISSEY': 'Josh Morrissey',
         'Mathew Bodie': 'Mat Bodie', 'MICHAEL FERLAND': 'Micheal Ferland', 'MICHAEL SANTORELLI' :'Mike Santorelli',
         'CHRISTOPHER BREEN': 'Chris Breen', 'BRYCE VAN BRABRANT': 'Bryce Van Brabant', 'ALEXANDER KILLORN': 'Alex Killorn',
         'JOSEPH MORROW': 'Joe Morrow', 'ALEX STEEN': 'Alexander Steen', 'BRADLEY MILLS': 'Brad Mills',
         'MICHAEL SISLO': 'Mike Sislo', 'MICHAEL VERNACE': 'Mike Vernace', 'STEVEN REINPRECHT': 'Steve Reinprecht',
         'MATTHEW MURRAY': 'Matt Murray', 'THOMAS MCCOLLUM': 'TOM MCCOLLUM', 'MICHAEL MATHESON': 'MIKE MATHESON',
         'BOO NIEVES': 'CRISTOVAL NIEVES', 'J.F. BERUBE': 'JEAN-FRANCOIS BERUBE', 'TONY DEANGELO': 'ANTHONY DEANGELO',
         'JEFFREY HAMILTON': 'JEFF HAMILTON', 'JAMES VANDERMEER': 'JIM VANDERMEER', 'MICHAEL YORK': 'MIKE YORK',
         'EMMANUEL LEGACE': 'MANNY LEGACE', 'JAMES DOWD': 'JIM DOWD', 'ANDREW MILLER': 'DREW MILLER',
         'JOHN PEVERLEY': 'RICH PEVERLEY', 'ILJA ZUBOV': 'ILYA ZUBOV', 'CHRISTOPHER MINARD': 'CHRIS MINARD',
         'BENJAMIN ONDRUS': 'BEN ONDRUS', 'ZACH FITZGERALD': 'ZACK FITZGERALD', 'STEPHEN VALIQUETTE': 'STEVE VALIQUETTE',
         'OLAF KOLZIG': 'OLIE KOLZIG', 'J-SEBASTIEN AUBIN': 'JEAN-SEBASTIEN AUBIN', 'ALEXANDER AULD': 'ALEX AULD',
         'JAMES HOWARD': 'JIMMY HOWARD', 'JEFF DROUIN-DESLAURIERS': 'JEFF DESLAURIERS', 'SIMEON VARLAMOV': 'SEMYON VARLAMOV',
         'ALEXANDER PECHURSKI': 'Alexander Pechurskiy', 'JEFFREY PENNER': 'JEFF PENNER', 'EMMANUEL FERNANDEZ': 'Manny FERNANDEZ',
         'ALEXANDER PETROVIC': 'ALEX PETROVIC', 'ZACHARY ASTON-REESE': 'ZACH ASTON-REESE', 'J-F BERUBE': 'JEAN-FRANCOIS BERUBE',
         "DANNY O'REGAN": "DANIEL O'REGAN", "PATRICK MAROON": "PAT MAROON", "LEE  STEMPNIAK": "LEE STEMPNIAK",
         "JAMES REIMER ,": "JAMES REIMER", "CALVIN PETERSEN ,": "CALVIN PETERSEN", "CAL PETERSEN": "CALVIN PETERSEN"
         }


def fix_name(name):
    """
    Check if a name falls under those that need fixing. If it does...fix it.

    :param name: name in pbp

    :return: Either the given parameter or the fixed name
    """
    return Names.get(name, name).upper()


def get_team(team):
    """
    Get the fucking team
    """
    return TEAMS.get(team, team).upper()


def get_season(date):
    """
    Get Season based on from_date

    :param date: date

    :return: season -> ex: 2016 for 2016-2017 season
    """
    year = date[:4]
    date = time.strptime(date, "%Y-%m-%d")

    if date > time.strptime('-'.join([year, '01-01']), "%Y-%m-%d"):
        if date < time.strptime('-'.join([year, '09-01']), "%Y-%m-%d"):
            return int(year) - 1
        else:
            return int(year)
    else:
        if date > time.strptime('-'.join([year, '07-01']), "%Y-%m-%d"):
            return int(year)
        else:
            return int(year) - 1


def convert_to_seconds(minutes):
    """
    Return minutes elapsed in time format to seconds elapsed

    :param minutes: time elapsed

    :return: time elapsed in seconds
    """
    if minutes == '-16:0-':
        return '1200'      # Sometimes in the html at the end of the game the time is -16:0-

    import datetime
    x = time.strptime(minutes.strip(' '), '%M:%S')

    return datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()


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
                                "\nPlease Try Again (you may need to try a few times before it works). ")
        else:
            print_warning("Timeout Error: The server took too long to respond to our request.")
            page = None

    # Pause for 1 second - make it more if you want
    time.sleep(1)

    return page


def print_warning(msg):
    """Print the Warning"""
    warnings.warn(msg)


def if_rescrape(user_rescrape):
    """
    If you want to re_scrape. If someone is a dumbass and feeds it a non-boolean it terminates the program

    Note: Only matters when you have a directory specified

    :param user_rescrape: Boolean

    :return: None
    """
    global re_scrape

    if isinstance(user_rescrape, bool):
        re_scrape = user_rescrape
    else:
        raise ValueError("Error: 'if_rescrape' must be a boolean. Not a {}".format(type(user_rescrape)))


def add_dir(user_dir):
    """
    Add directory to store scraped docs if valid. Or create in the home dir

    NOTE: After this functions docs_dir is either None or a valid directory

    :param user_dir: If bool=True create in the home dire or if user provided directory on their machine

    :return: None
    """
    global docs_dir

    # False so they don't want it
    if not user_dir:
        docs_dir = False
        return

    # Something was given
    # Either True or stirng to directory
    # We tell by the type
    # If boolean refer to the home directory
    if isinstance(user_dir, bool):
        docs_dir = os.path.join(os.path.expanduser('~'), "hockey_scraper_data")
        # Create if needed
        if not os.path.isdir(docs_dir):
            print_warning("Creating the hockey_scraper_data directory in the home directory")
            os.mkdir(docs_dir)
    elif isinstance(user_dir, str) and os.path.isdir(user_dir):
        docs_dir = user_dir
    elif not (isinstance(user_dir, str) and isinstance(user_dir, bool)):
        docs_dir = False
        print_warning("The docs_dir argument provided is invalid")
    else:
        docs_dir = False
        print_warning("The directory specified for the saving of scraped docs doesn't exist. Therefore:"
              "\n1. All specified games will be scraped from their appropriate sources (NHL or ESPN)."
              "\n2. All scraped files will NOT be saved at all. Please either create the directory you want them to be "
              "deposited in or recheck the directory you typed in and start again.\n")


def get_file(file_info):
    """
    Get the specified file.

    If a docs_dir is provided we check if it exists. If it does we see if it contains that page (and saves if it
    doesn't). If the docs_dir doesn't exist we just scrape from the source and not save.

    :param file_info: Dictionary containing the info for the file.
                      Contains the url, name, type, and season

    :return: page
    """
    original_path = os.getcwd()
    file_info['dir'] = docs_dir

    # If something is provided...we try to change the cwd
    if file_info['dir']:
        os.chdir(file_info['dir'])

    # If everything checks out we'll retrieve it, otherwise we scrape it
    if docs_dir and sp.check_file_exists(file_info) and re_scrape is False:
        page = sp.get_page(file_info)
    else:
        page = scrape_page(file_info['url'])
        sp.save_page(page, file_info, docs_dir)

    # Change back to current cwd to avoid any potential issues
    os.chdir(original_path)

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


def to_csv(base_file_name, pbp_df, shifts_df, league):
    """
    Write DataFrame(s) to csv file(s)

    :param base_file_name: name of file
    :param pbp_df: pbp DataFrame
    :param shifts_df: shifts DataFrame
    :param league: nhl or nwhl

    :return: None
    """
    pbp_file = shifts_file = base_file_name

    # This was a late addition so we add support here
    if isinstance(docs_dir, str) and not os.path.isdir(os.path.join(docs_dir, "csvs")):
        os.mkdir(os.path.join(docs_dir, "csvs"))

    if pbp_df is not None:
        if isinstance(docs_dir, str):
            pbp_file = os.path.join(docs_dir, "csvs", '{}_pbp{}.csv'.format(league, base_file_name))
        else:
            pbp_file = '{}_pbp{}.csv'.format(league, pbp_file)

        print("\nPbp data deposited in file - " + pbp_file)
        pbp_df.to_csv(pbp_file, sep=',', encoding='utf-8')
    if shifts_df is not None:
        if isinstance(docs_dir, str):
            shifts_file = os.path.join(docs_dir, "csvs", '{}_shifts{}.csv'.format(league, base_file_name))
        else:
            shifts_file = '{}_shifts{}.csv'.format(league, shifts_file)

        print("Shift data deposited in file - " + shifts_file)
        shifts_df.to_csv(shifts_file, sep=',', encoding='utf-8')
