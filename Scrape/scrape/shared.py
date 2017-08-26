import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


"""
This file is a bunch of the shared functions or just general stuff used by the different scrapers
in the scrape directory
"""


TEAMS = {
    'ANAHEIM DUCKS': 'ANA',
    'ARIZONA COYOTES': 'ARI',
    'ATLANTA THRASHERS': 'ATL',
    'BOSTON BRUINS': 'BOS',
    'BUFFALO SABRES': 'BUF',
    'CAROLINA HURRICANES': 'CAR',
    'COLUMBUS BLUE JACKETS': 'CBJ',
    'CALGARY FLAMES': 'CGY',
    'CHICAGO BLACKHAWKS': 'CHI',
    'COLORADO AVALANCHE': 'COL',
    'DALLAS STARS': 'DAL',
    'DETROIT RED WINGS': 'DET',
    'EDMONTON OILERS': 'EDM',
    'FLORIDA PANTHERS': 'FLA',
    'LOS ANGELES KINGS': 'L.A',
    'MINNESOTA WILD': 'MIN',
    'MONTREAL CANADIENS': 'MTL',
    'MONTRÉAL CANADIENS': 'MTL',
    'NEW JERSEY DEVILS': 'N.J',
    'NASHVILLE PREDATORS': 'NSH',
    'NEW YORK ISLANDERS': 'NYI',
    'NEW YORK RANGERS': 'NYR',
    'OTTAWA SENATORS': 'OTT',
    'PHILADELPHIA FLYERS': 'PHI',
    'PHOENIX COYOTES': 'PHX',
    'PITTSBURGH PENGUINS': 'PIT',
    'SAN JOSE SHARKS': 'S.J',
    'ST. LOUIS BLUES': 'STL',
    'TAMPA BAY LIGHTNING': 'T.B',
    'TORONTO MAPLE LEAFS': 'TOR',
    'VANCOUVER CANUCKS': 'VAN',
    'VEGAS GOLDEN KNIGHTS': 'VGK',
    'WINNIPEG JETS': 'WPG',
    'WASHINGTON CAPITALS': 'WSH'
}


"""
Fixes some of the mistakes made with player names

A majority of this is courtesy of Muneeb Alam (on twitter: @muneebalamcu)
Found here -> https://github.com/muneebalam/Hockey/blob/master/NHL/Core/GetPbP.py
"""

NAMES = {
    'n/a': 'n/a',
    'AARON MACKENZIE': 'Aaron MacKenzie',
    'ADAM MCQUAID': 'Adam McQuaid',
    'AJ GREER': 'A.J. Greer',
    'ALEXANDER FROLOV': 'Alex Frolov',
    'ALEXANDER KHOKHLACHEV': 'Alex Khokhlachev',
    'ALEXANDER KILLORN': 'Alex Killorn',
    'ALEXANDER OVECHKIN': 'Alex Ovechkin',
    'ALEXANDRE BURROWS': 'Alex Burrows',
    'ALEXEI KOVALEV': 'Alex Kovalev',
    'ALEX STEEN': 'Alexander Steen',
    'ANDREI KASTSITSYN': 'Andrei Kostitsyn',
    'ANDREW GREENE': 'Andy Greene',
    'ANDREW MACDONALD': 'Andrew MacDonald',
    'ANDREW MACWILLIAM': 'Andrew MacWilliam',
    'ANDREW WOZNIEWSKI': 'Andy Wozniewski',
    'ANDY MCDONALD': 'Andy McDonald',
    'BATES (JON) BATTAGLIA': 'Bates Battaglia',
    'B.J CROMBEEN': 'B.J. Crombeen',
    'BJ CROMBEEN': 'B.J. Crombeen',
    'BRADLEY MILLS': 'Brad Mills',
    'BRANDON CROMBEEN': 'B.J. Crombeen',
    'BRANDON MCMILLAN': 'Brandon McMillan',
    'BRAYDEN MCNABB': 'Brayden McNabb',
    'BRETT MACLEAN': 'Brett MacLean',
    'BRETT MCLEAN': 'Brett McLean',
    'BRIAN MCGRATTAN': 'Brian McGrattan',
    'BROCK MCGINN': 'Brock McGinn',
    'BRYAN MCCABE': 'Bryan McCabe',
    'BRYCE VAN BRABANT': 'Bryce van Brabant',
    'BRYCE VAN BRABRANT': 'Bryce Van Brabant',
    'CALVIN DE HAAN': 'Calvin de Haan',
    'CAMERON BARKER': 'Cam Barker',
    'CARSON MCMILLAN': 'Carson McMillan',
    'CHRIS TANEV': 'Christopher Tanev',
    'CHRISTOPHER BOURQUE': 'Chris Bourque',
    'CHRISTOPHER BREEN': 'Chris Breen',
    'CHRISTOPHER HIGGINS': 'Chris Higgins',
    'CHRISTOPHER NEIL': 'Chris Neil',
    'CHRIS VANDE VELDE': 'Chris VandeVelde',
    'CLARKE MACARTHUR': 'Clarke MacArthur',
    'CODY MCCORMICK': 'Cody McCormick',
    'CODY MCLEOD': 'Cody McLeod',
    'COLIN (JOHN) WHITE': 'Colin White',
    'COLIN MCDONALD': 'Colin McDonald',
    'CONNOR MCDAVID': 'Connor McDavid',
    'CRAIG MACDONALD': 'Craig MacDonald',
    'CURTIS MCKENZIE': 'Curtis McKenzie',
    'DANIEL BRIERE': 'Danny Briere',
    'DANIEL CARCILLO': 'Dan Carcillo',
    'DANIEL CLEARY': 'Dan Cleary',
    'DANIEL GIRARDI': 'Dan Girardi',
    'DAN LACOUTURE': 'Dan LaCouture',
    'DANNY CLEARY': 'Dan Cleary',
    'DANNY DEKEYSER': 'Danny DeKeyser',
    'DARREN MCCARTY': 'Darren McCarty',
    'DAVID JOHNNY ODUYA': 'Johnny Oduya',
    'DAVID MCINTYRE': 'David McIntyre',
    'DAVID VAN DER GULIK': 'David van der Gulik',
    'DEAN MCAMMOND': 'Dean McAmmond',
    'DENIS GAUTHIER JR.': 'Denis Gauthier Jr.',
    'DEREK MACKENZIE': 'Derek MacKenzie',
    'DEVANTE SMITH-PELLY': 'Devante Smith-Pelly',
    'DJ KING': 'DJ King',
    'Dwayne KING': 'DJ King',
    'DYLAN MCILRATH': 'Dylan McIlrath',
    'EDWARD PURCELL': 'Teddy Purcell',
    'EVGENII DADONOV': 'Evgeny Dadonov',
    'FRAZER MCLAREN': 'Frazer McLaren',
    'FREDDY MODIN': 'Fredrik Modin',
    'FREDERICK MEYER IV': 'Freddy Meyer',
    'FRÉDÉRIC ST-DENIS': 'Frederic St-Denis',
    'GREG MCKEGG': 'Greg McKegg',
    'HARRISON ZOLNIERCZYK': 'Harry Zolnierczyk',
    'ILJA BRYZGALOV': 'Ilya Bryzgalov',
    'JACOB DE LA ROSE': 'Jacob de la Rose',
    'JACOB DOWELL': 'Jake Dowell',
    'JAKE MCCABE': 'Jake McCabe',
    'JAMES VAN RIEMSDYK': 'James van Riemsdyk',
    'JAMES WYMAN': 'JT Wyman',
    'JAMIE MCBAIN': 'Jamie McBain',
    'JAMIE MCGINN': 'Jamie McGinn',
    'JARED MCCANN': 'Jared McCann',
    'JAY MCCLEMENT': 'Jay McClement',
    'JAY MCKEE': 'Jay McKee',
    'JEAN-FRANCOIS JACQUES': 'JF Jacques',
    'JEAN-GABRIEL PAGEAU': 'Jean-Gabriel Pageau',
    'JEAN-PHILIPPE COTE': 'Jean-Philippe Cote',
    'JEAN-PIERRE DUMONT': 'JP Dumont',
    'J-F JACQUES': 'JF Jacques',
    'JOE DIPENTA': 'Joe DiPenta',
    'JOEY MACDONALD': 'Joey MacDonald',
    'JOHN HILLEN III': 'Jack Hillen',
    'JOHN MCCARTHY': 'John McCarthy',
    'JOHN-MICHAEL LILES': 'John-Michael Liles',
    'JOHN ODUYA': 'Johnny Oduya',
    'JONATHAN AUDY-MARCHESSAULT': 'Jonathan Marchessault',
    'JONATHAN SIM': 'Jon Sim',
    'JONATHON KALINSKI': 'Jon Kalinski',
    'JON DISALVATORE': 'Jon DiSalvatore',
    'JORDAN LAVALLEE-SMOTHERMAN': 'Jordan Lavallee-Smotherman',
    'JOSEPH CORVO': 'Joe Corvo',
    'JOSEPH CRABB': 'Joey Crabb',
    'JOSEPH MORROW': 'Joe Morrow',
    'JOSHUA BAILEY': 'Josh Bailey',
    'JOSHUA HENNESSY': 'Josh Hennessy',
    'JOSHUA MORRISSEY': 'Josh Morrissey',
    'J P DUMONT': 'JP Dumont',
    'J-P DUMONT': 'JP Dumont',
    'JP DUMONT': 'JP Dumont',
    'J.T. BROWN': 'JT Brown',
    'JT COMPHER': 'J.T. Compher',
    'J.T. MILLER': 'JT Miller',
    'JT WYMAN': 'JT Wyman',
    'KENNDAL MCARDLE': 'Kenndal McArdle',
    'KRISTOPHER LETANG': 'Kris Letang',
    'KRYS BARCH': 'Krystofer Barch',
    'KRYSTOFER KOLANOS': 'Krys Kolanos',
    'KYLE MCLAREN': 'Kyle McLaren',
    'LANE MACDERMID': 'Lane MacDermid',
    'MAKSIM MAYOROV': 'Maxim Mayorov',
    'MARC-ANDRE BERGERON': 'Marc-Andre Bergeron',
    'MARC-ANDRE BOURDON': 'Marc-Andre Bourdon',
    'MARC-ANDRE CLICHE': 'Marc-Andre Cliche',
    'MARC-ANDRE FLEURY': 'Marc-Andre Fleury',
    'MARC-ANDRE GRAGNANI': 'Marc-Andre Gragnani',
    'MARC-ANTOINE POULIOT': 'Marc-Antoine Pouliot',
    'MARC-EDOUARD VLASIC': 'Marc-Edouard Vlasic',
    'MARC POULIOT': 'Marc-Antoine Pouliot',
    'MARK VAN GUILDER': 'Mark van Guilder',
    'MARTIN ST LOUIS': 'Martin St. Louis',
    'MARTIN ST PIERRE': 'Martin St. Pierre',
    'MARTY HAVLAT': 'Martin Havlat',
    'Mathew Bodie': 'Mat Bodie',
    'MATHEW DUBMA': 'Matt Dumba',
    'MATHEW DUMBA': 'Matt Dumba',
    'MATTHEW BENNING': 'Matt Benning',
    'MATTHEW CARLE': 'Matt Carle',
    'MATTHEW IRWIN': 'Matt Irwin',
    'MATTHEW MURRAY': 'Matt Murray',
    'MATTHEW NIETO': 'Matt Nieto',
    'MATTHEW STAJAN': 'Matt Stajan',
    'MAXIME TALBOT': 'Max Talbot',
    'MAX MCCORMICK': 'Max McCormick',
    'MAXWELL REINHART': 'Max Reinhart',
    'MICHAEL BLUNDEN': 'Mike Blunden',
    'MICHAËL BOURNIVAL': 'Michael Bournival',
    'MICHAEL CAMMALLERI': 'Mike Cammalleri',
    'MICHAEL FERLAND': 'Micheal Ferland',
    'MICHAEL GRIER': 'Mike Grier',
    'MICHAEL KNUBLE': 'Mike Knuble',
    'MICHAEL KOMISAREK': 'Mike Komisarek',
    'MICHAEL MCCARRON': 'Michael McCarron',
    'MICHAEL MODANO': 'Mike Modano',
    'MICHAEL RUPP': 'Mike Rupp',
    'MICHAEL SANTORELLI': 'Mike Santorelli',
    'MICHAEL SILLINGER': 'Mike Sillinger',
    'MICHAEL SISLO': 'Mike Sislo',
    'MICHAEL VERNACE': 'Mike Vernace',
    'MICHÃ«L BOURNIVAL': 'Michael Bournival',
    'MIKE MCKENNA': 'Mike McKenna',
    'MIKE VAN RYN': 'Mike van Ryn',
    'NATHAN GUENIN': 'Nate Guenin',
    'NATHAN MACKINNON': 'Nathan MacKinnon',
    'NATHAN MCIVER': 'Nathan McIver',
    'NICHOLAS BOYNTON': 'Nick Boynton',
    'NICHOLAS DRAZENOVIC': 'Nick Drazenovic',
    'NICKLAS BERGFORS': 'Niclas Bergfors',
    'NICKLAS GROSSMAN': 'Nicklas Grossmann',
    'NICOLAS PETAN': 'Nic Petan',
    'NIKLAS KRONVALL': 'Niklas Kronwall',
    'NIKOLAI ANTROPOV': 'Nik Antropov',
    'NIKOLAY KULEMIN': 'Nikolai Kulemin',
    'NIKOLAY ZHERDEV': 'Nikolai Zherdev',
    'OLE-KRISTIAN TOLLEFSEN': 'Ole-Kristian Tollefsen',
    'OLIVER EKMAN-LARSSON': 'Oliver Ekman-Larsson',
    'OLIVIER MAGNAN-GRENIER': 'Olivier Magnan-Grenier',
    'OLIVIER MAGNAN': 'Olivier Magnan-Grenier',
    'PA PARENTEAU': 'PA Parenteau',
    'PER JOHAN AXELSSON': 'PJ Axelsson',
    'PER-JOHAN AXELSSON': 'PJ Axelsson',
    'PERNELL KARL SUBBAN': 'PK Subban',
    'PHILIP MCRAE': 'Philip McRae',
    'PHILIP VARONE': 'Phil Varone',
    'PIERRE ALEXANDRE PARENTEAU': 'PA Parenteau',
    'PIERRE-ALEXANDRE PARENTEAU': 'PA Parenteau',
    'PIERRE-CEDRIC LABRIE': 'Pierre-Cedric Labrie',
    'PIERRE-EDOUARD BELLEMARE': 'Pierre-Edouard Bellemare',
    'PIERRE-LUC LETOURNEAU-LEBLOND': 'Pierre Leblond',
    'PIERRE-MARC BOUCHARD': 'Pierre-Marc Bouchard',
    'PIERRE PARENTEAU': 'Pierre Parenteau',
    'P. J. AXELSSON': 'PJ Axelsson',
    'P.K. SUBBAN': 'PK Subban',
    'PK SUBBAN': 'PK Subban',
    'RAYMOND MACIAS': 'Ray Macias',
    'RICK DIPIETRO': 'Rick DiPietro',
    'R.J UMBERGER': 'RJ Umberger',
    'R.J. UMBERGER': 'RJ Umberger',
    'RJ UMBERGER': 'RJ Umberger',
    'ROBERT BLAKE': 'Rob Blake',
    'ROBERT EARL': 'Robbie Earl',
    'ROBERT HOLIK': 'Bobby Holik',
    'ROBERT SCUDERI': 'Rob Scuderi',
    'RODNEY PELLEY': 'Rod Pelley',
    'RYAN MCDONAGH': 'Ryan McDonagh',
    'RYAN NUGENT-HOPKINS': 'Ryan Nugent-Hopkins',
    'SIARHEI KASTSITSYN': 'Sergei Kostitsyn',
    'STAFFAN KRONVALL': 'Staffan Kronwall',
    'STEVE MACINTYRE': 'Steve MacIntyre',
    'STEVE MCCARTHY': 'Steve McCarthy',
    'STEVEN REINPRECHT': 'Steve Reinprecht',
    'TIMOTHY JR. THOMAS': 'Tim Thomas',
    'T.J. BRENNAN': 'TJ Brennan',
    'TJ BRENNAN': 'TJ Brennan',
    'TJ BRODIE': 'TJ Brodie',
    'T.J. GALIARDI': 'TJ Galiardi',
    'TJ GALIARDI': 'TJ Galiardi',
    'TJ Hensick': 'TJ Hensick',
    'T.J. HENSICK': 'TJ Hensick',
    'T.J. OSHIE': 'TJ Oshie',
    'TJ OSHIE': 'TJ Oshie',
    'TOBY ENSTROM': 'Tobias Enstrom',
    'TOMMY SESTITO': 'Tom Sestito',
    'TREVOR VAN RIEMSDYK': 'Trevor van Riemsdyk',
    'TYE MCGINN': 'Tye McGinn',
    'VACLAV PROSPAL': 'Vinny Prospal',
    'VINCENT HINOSTROZA': 'Vinnie  Hinostroza',
    'VOJTEK VOLSKI': 'Wojtek Wolski',
    'VYACHESLAV VOYNOV': 'Slava Voynov',
    'WILLIAM THOMAS': 'Bill Thomas',
    'ZACHARY SANFORD': 'Zach Sanford',
    'ZACHERY STORTINI': 'Zack Stortini',
}


def fix_name(name):
    """
    Check if a name falls under those that need fixing.
    If it does...fix it
    :param name: name in pbp
    :return: Either the given parameter or the fixed name
    """
    if name in NAMES:
        return NAMES[name].upper()
    else:
        return name


def convert_to_seconds(value):
    """
    Convert a time string into seconds

    :param value: `str` representing the time; typically in the format 'MM:SS'
    :return: time in seconds
    """
    stripped = value.strip()

    # Sometimes in the html at the end of the game the time is -16:0-
    if stripped == '-16:0-':
        return 1200

    minutes, seconds = [int(piece) for piece in stripped.split(':', 1)]
    return 60 * minutes + seconds


session = requests.Session()
retries = Retry(total=10, backoff_factor=.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def get_url(url):
    """
    Get the url

    :param url: given url
    :return: page
    """
    response = session.get(url, timeout=5)
    response.raise_for_status()

    return response
