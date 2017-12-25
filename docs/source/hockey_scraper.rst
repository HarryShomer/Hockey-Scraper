hockey_scraper
==============

The hockey_scraper module contains all of the functions used for scraping.

Scraping
--------

There are three ways to scrape games:

\1. *Scrape by Season*:

Scrape games on a season by season level (Note: A given season is referred to by the first of the two years it spans.
So you would refer to the 2016-2017 season as 2016).
::

    import hockey_scraper

    # Scrapes the 2015 & 2016 season with shifts and stores the data in a Csv file (both are equivalent!!!)
    hockey_scraper.scrape_seasons([2015, 2016], True)
    hockey_scraper.scrape_seasons([2015, 2016], True, data_format='Csv')

    # Scrapes the 2008 season without shifts and returns a json string of the data
    scraped_data = hockey_scraper.scrape_seasons([2008], False, data_format='Json')

    # Scrapes 2014 season without shifts including preseason games
    hockey_scraper.scrape_seasons([2014], False, preseason=True)

\2. *Scrape by Game*:

Scrape a list of games provided. All game ID's can be found using `this link
<https://statsapi.web.nhl.com/api/v1/schedule?startDate=2016-10-03&endDate=2017-06-20>`_
(you need to play around with the dates in the url).
::

    import hockey_scraper

    # Scrapes the first game of 2014, 2015, and 2016 seasons with shifts and stores the data in a Csv file
    hockey_scraper.scrape_games([2014020001, 2015020001, 2016020001], True)

    # Scrapes the first game of 2007, 2008, and 2009 seasons with shifts and returns a Json string of the data
    scraped_data = hockey_scraper.scrape_games([2007020001, 2008020001, 2009020001], True, data_format='Json')

\3. *Scrape by Date Range*:

Scrape all games between a specified date range. All dates must be written in a "yyyy-mm-dd" format.
::

    import hockey_scraper

    # Scrapes all games between date range without shifts and stores the data in a Csv file (both are equivalent!!!)
    hockey_scraper.scrape_date_range('2016-10-10', '2016-10-20', False)
    hockey_scraper.scrape_date_range('2016-10-10', '2016-10-20', False, preseason=False)

    # Scrapes all games between 2015-1-1 and 2015-1-15 without shifts and returns a Json string of the data
    scraped_data = hockey_scraper.scrape_date_range('2015-1-1', '2015-1-15', False, data_format='Json')

    # Scrapes all games from 2014-09-15 to 2014-11-01 with shifts including preseason games
    hockey_scraper.scrape_date_range('2014-09-15', '2014-11-01', True, preseason=True)


**Notes**:

\1. For all three functions you must specify if you want to also scrape shifts (TOI tables) with a boolean. The Play by
Play is automatically scraped.

\2. When scraping by date range or by season, preseason games aren't scraped unless otherwise specified.

\3. For all three functions the scraped data is deposited into a Csv file unless it's specified to return it as a Json string.

\4. The Json string returned is structured like so:
::


   # When scraping by game or date range
   "
   {
      'pbp': [
         Plays
      ],
      'shifts': [
         Shifts
      ]
   }
   "

   # When scraping by season
   "
   {
      'pbp': {
         'Seasons': [
            Plays
         ]
      },
      'shifts': {
         'Seasons': [
            Plays
         ]
      }
   }
   "

   # For example, if you scraped the 2008 and 2009 seasons the Json will look like this:
   "
   {
      'pbp': {
         '2008': [
            Plays
         ],
         '2009': [
            Plays
         ]
      },
      'shifts': {
         '2008': [
            Shifts
         ],
         '2009': [
            Shifts
         ]
      }
   }
   "


Functions
---------
.. _Functions:

Scrape Functions
~~~~~~~~~~~~~~~~
.. automodule:: hockey_scraper.scrape_functions
   :members:

Game Scraper
~~~~~~~~~~~~
.. automodule:: hockey_scraper.game_scraper
   :members:

Html PBP
~~~~~~~~
.. automodule:: hockey_scraper.html_pbp
   :members:

Json PBP
~~~~~~~~
.. automodule:: hockey_scraper.json_pbp
   :members:

Espn PBP
~~~~~~~~
.. automodule:: hockey_scraper.espn_pbp
   :members:

Json Shifts
~~~~~~~~~~~
.. automodule:: hockey_scraper.json_shifts
   :members:

Html Shifts
~~~~~~~~~~~
.. automodule:: hockey_scraper.html_shifts
   :members:

Schedule
~~~~~~~~
.. automodule:: hockey_scraper.json_schedule
   :members:

Playing Roster
~~~~~~~~~~~~~~
.. automodule:: hockey_scraper.playing_roster
   :members:

Shared Functions
~~~~~~~~~~~~~~~~
.. automodule:: hockey_scraper.shared
   :members:
