"""
Scrape the schedule info for nwhl games
"""
import datetime
import re
from bs4 import BeautifulSoup
import hockey_scraper.utils.shared as shared


def get_schedule(url, name):
    """
    Given a date it returns the raw html

    :param url: url for page
    :param name: Name for saved file

    :return: raw html of game
    """
    page_info = {
        "url": url,
        "name": str(name),
        "type": "html_schedule_nwhl",
        "season": "nwhl",
    }

    return shared.get_file(page_info)


def date_obj(date):
    """
    Convert date string to a datetime object
    
    :param date: e.g. 2015-10-20
    
    :return: Datetime object
    """
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def get_date_games(date_info):
    """
    Get all the games corresponding to a certain date
    
    :param date_info: Page info for that date
    
    :return: All games for that day
    """
    base = "https://www.nwhl.zone/"
    response = get_schedule(base + date_info['url'], date_info['date'])
    soup = BeautifulSoup(response, "lxml")

    tables = soup.find_all("table", {"class": "statTable sortable noSortImages"})
    trs = tables[0].find("tbody").find_all("tr")

    # Each tr is a game
    games = []
    for tr in trs:
        # For finding the game id
        game_id_regex = re.compile(r"row_(\d+)")

        # Get all other game info nested inside
        tds = tr.find_all("td")
        status = tds[5].text.strip()

        # Only append if the game already started/finished
        # If scheduled will have starting time
        if status == '':
            games.append({
                "game_id": game_id_regex.findall(tr['id'])[0],
                "date": date_info['date'],
                "sub_type": date_info['sub_type'],
                "away_team": tds[0].text.strip(),
                "away_score": tds[1].text.strip(),
                "home_team": tds[2].text.strip(),
                "home_score": tds[3].text.strip(),
                "location": tds[4].text.strip(),
            })

    return games


def get_sub_dates(url, season, sub_type):
    """
    Get dates of games off of sub-season page
    
    :param url: Url for sub-season 
    :param season: Given season
    :param sub_type: e.g. Regular Season
    
    :return: List with all dates of games
    """
    soup = BeautifulSoup(get_schedule(url, "-".join([str(season), sub_type])), "lxml")
    divs = soup.find_all("div", {"class": "games-slider-group"})
    lis = [div.find_all("li") for div in divs]

    # Get all dates that have games
    dates = []
    for month in lis:
        for day in month:
            dates.append({
                "date": datetime.datetime.strptime(str(day['id'])[str(day['id']).find("day_") + len("days"):], '%Y_%m_%d').strftime('%Y-%m-%d'),
                "url": day.find("a")['href'],
                "sub_type": sub_type.strip()
            })

    return dates


def get_dates(from_date, to_date):
    """
    Get all the date pages that a game occurs in the range
    
    :param from_date: Date Scrape from
    :param to_date: Date scrape to 
    
    :return: List of Dates where games occurred 
    """
    date_range = from_date + "-" + to_date

    # Get initial info
    # Just use 2015 season
    seed_url = "https://www.nwhl.zone/schedule/day/league_instance/46947"
    soup = BeautifulSoup(get_schedule(seed_url, date_range + "-seed"), "lxml")

    # By Season (e.g. 2017-2018)
    sub_seasons = {season['label']: season.find_all("option") for season in soup.find_all("optgroup")}

    # Add Current season (here 2015 subs) - not found in above dropdown
    cur_season_subs = soup.find_all("div", {"class": "currentSeason"})[0].find_all("a")
    cur_season_subs = [sub for sub in cur_season_subs if sub['class'][0] != "close"]
    cur_season = soup.find_all("div", {"class": "currentSeason"})[0].find("span").text.strip()[:9]
    sub_seasons[cur_season] = cur_season_subs

    # Season o first date to season of last date
    # Know way to index by date so we start from the season
    from_season = shared.get_season(from_date)
    to_season = shared.get_season(to_date)

    # Get all dates for that season range (season of from_date and season of to_date)
    base = "https://www.nwhl.zone/"
    dates = []
    for season in range(from_season, to_season + 1):
        for sub in sub_seasons["-".join([str(season), str(season + 1)])]:
            # Get dates for season-sub_type combo
            # Href and value are due to current season
            try:
                sub_dates = get_sub_dates(base + sub['value'], str(season), sub.text)
            except KeyError:
                sub_dates = get_sub_dates(base + sub['href'], str(season), sub.text)
            for sub_date in sub_dates:
                # Only add dates in range
                if date_obj(sub_date['date']) >= date_obj(from_date) and date_obj(sub_date['date']) <= date_obj(to_date):
                    dates.append(sub_date)

    return dates


def scrape_dates(from_date, to_date):
    """
    Get all the games between two dates
    
    :param from_date: Date Scrape from
    :param to_date: Date scrape to
    
    :return: List of all games
    """
    games = []
    for game_date in get_dates(from_date, to_date):
        games.extend(get_date_games(game_date))

    return games

