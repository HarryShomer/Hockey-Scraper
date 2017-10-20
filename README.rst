Hockey Scraper
==============

This project is designed to allow people to scrape Play by Play and
Shift data off of the National Hockey League (NHL) API and website for
all regular season and playoff games since the 2010-2011 season (further
testing needs to be done to ensure it works for earlier seasons).

Prerequisites
-------------

You are going to need to have python installed for this. Specifically,
you’ll need from at least version 3.6.0.

If you don’t have python installed on your machine, I’d recommend
installing it through the anaconda distribution (here -
https://www.continuum.io/downloads). Anaconda comes with a bunch of
libraries pre-installed so it’ll be easier to start off.

How to Use
----------

To install just open up your terminal and type in:

::

    pip install hockey_scraper


To use it just open up python:

::

    python


And once inside import the package:

::

    import hockey_scraper


There are three relevant functions used for scraping data (After any
scraping function finishes running, the data scraped can be found in the
folder which contains your code):

**1. scrape\_seasons:**

This function is used to scrape on a season by season level. It takes
two arguments:

1. ‘seasons’ - List of seasons you want to scrape (Note: A given season
   is referred to by the first of the two years it spans. So you would
   refer to the 2016-2017 season as 2016.

2. ‘if\_scrape\_shifts’ - Boolean indicating whether or not you want to
   scrape the shifts too. ::

       # Scrapes 2015 & 2016 season with shifts
       hockey_scraper.scrape_seasons([2015, 2016], True)

       # Scrapes 2016 season without shifts
       hockey_scraper.scrape_seasons([2016], False)

**2. scrape\_games:**

This function is used to scrape any collection of games you want. It
takes two arguments:

1. ‘games’ - List of games you want to scrape. A game is identified by
   the game id used by the NHL (ex: 2016020001). The list of
   corresponding id’s for games can be found here
   (https://statsapi.web.nhl.com/api/v1/schedule?startDate=2016-10-12&endDate=2016-10-12
   - Just fiddle with the start and end dates in the url to find the
   game you are looking for).

2. ‘if\_scrape\_shifts’ - Boolean indicating whether or not you want to
   scrape the shifts too. ::

       # Scrapes first game of 2014, 2015, and 2016 seasons with shifts
       hockey_scraper.scrape_games([2014020001, 2015020001, 2016020001], True)

**3. scrape\_date\_range:**

This functions is used to scrape any games in a given date range. All
dates must be written in the following format yyyy-mm-dd (ex:
‘2016-10-20’). It take three arguments:

1. ‘from\_date’ - Date of beginning of interval you want to scrape

2. ‘to\_date’ - Date of end of interval you want to scrape

3. ‘if\_scrape\_shifts’ - Boolean indicating whether or not you want to scrape the shifts too. ::

        # Scrapes games between 2016-10-10 and 2016-10-20 without shifts
        hockey_scraper.scrape_date_range('2016-10-10', '2016-10-20', False)



   





