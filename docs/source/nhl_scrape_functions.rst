NHL Scraping Functions
======================

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

    # Scrapes the 2008 season without shifts and returns a dictionary with the DataFrame
    scraped_data = hockey_scraper.scrape_seasons([2008], False, data_format='Pandas')

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

    # Scrapes the first game of 2007, 2008, and 2009 seasons with shifts and returns a a dictionary with the DataFrames
    scraped_data = hockey_scraper.scrape_games([2007020001, 2008020001, 2009020001], True, data_format='Pandas')

\3. *Scrape by Date Range*:

Scrape all games between a specified date range. All dates must be written in a "yyyy-mm-dd" format.
::

    import hockey_scraper

    # Scrapes all games between date range without shifts and stores the data in a Csv file (both are equivalent!!!)
    hockey_scraper.scrape_date_range('2016-10-10', '2016-10-20', False)
    hockey_scraper.scrape_date_range('2016-10-10', '2016-10-20', False, preseason=False)

    # Scrapes all games between 2015-1-1 and 2015-1-15 without shifts and returns a a dictionary with the DataFrame
    scraped_data = hockey_scraper.scrape_date_range('2015-1-1', '2015-1-15', False, data_format='Pandas')

    # Scrapes all games from 2014-09-15 to 2014-11-01 with shifts including preseason games
    hockey_scraper.scrape_date_range('2014-09-15', '2014-11-01', True, preseason=True)


**Saving Files**

The option also exists to save the scraped files in another directory. This would speed up re-scraping any games since
we already have the docs needed for it. It would also be useful if you want to grab any extra information from them
as some of them contain a lot more information. In order to do this you can use the 'docs_dir' keyword. One can specify
the boolean value True to either create or refer (to an already created) directory in the home directory called
hockey_scraper data. Or you can specify the directory with the string of the path. If this is a valid directory,
when scraping each page it would first check if it was already scraped (therefore saving us the time of scraping it).
If it hasn't been scraped yet, it will then grab it from the source and save it in the given directory.

Sometimes you may have already scraped and saved a file but you want to re-scrape it from the source and save it again
(this may seem strange but the NHL frequently fixes mistakes so you may want to update what you have). This can be done
by setting the keyword argument rescrape equal to True.

::

    import hockey_scraper

    # Path to the given directory
    # Can also be True if you want the scraper to take care of it
    USER_PATH = "/...."

    # Scrapes the 2015 & 2016 season with shifts and stores the data in a Csv file
    # Also includes a path for an existing directory for the scraped files to be placed in or retrieved from.
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=USER_PATH)

    # Once could chose to re-scrape previously saved files by making the keyword argument rescrape=True
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=USER_PATH, rescrape=True)


**Additional Notes**:

\1. For all three functions you must specify if you want to also scrape shifts (TOI tables) with a boolean. The Play by
Play is automatically scraped.

\2. When scraping by date range or by season, preseason games aren't scraped unless otherwise specified. Also preseason
games are scraped at your own risk. There is no guarantee it will work or that the files are even there!!!

\3. For all three functions the scraped data is deposited into a Csv file unless it's specified to return the DataFrames

\4. The Dictionary with the DataFrames (and scraping errors) returned by setting data_format='Pandas' is structured like:
::

   {
      # Both of these are always included
      'pbp': pbp_df,
      'errors': scraping_errors,

      # This is only included when the argument 'if_scrape_shifts' is set equal to True
      'shifts': shifts_df
    }

\5. When including a directory, it must be a valid directory. It will not create it for you. You'll get an error message
but otherwise it will scrape as if no directory was provided.



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

Save Pages
~~~~~~~~~~
.. automodule:: hockey_scraper.save_pages
   :members:

Shared Functions
~~~~~~~~~~~~~~~~
.. automodule:: hockey_scraper.shared
   :members:
