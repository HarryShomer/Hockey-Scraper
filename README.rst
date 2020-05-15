.. image:: https://badge.fury.io/py/hockey-scraper.svg
   :target: https://badge.fury.io/py/hockey-scraper
.. image:: https://readthedocs.org/projects/hockey-scraper/badge/?version=latest
   :target: https://readthedocs.org/projects/hockey-scraper/?badge=latest
   :alt: Documentation Status


Hockey-Scraper
==============

.. inclusion-marker-for-sphinx


**Notes:**
 * Coordinates are only scraped from ESPN for versions 1.33+
 * NWHL usage has been deprecated due to the removal of the pbp information for each game.


Purpose
-------

This package is designed to allow people to scrape both NHL data. One can scrape the Play by Play
and Shift data off of the National Hockey League (NHL) API and website for all preseason, regular season, and playoff
games since the 2007-2008 season. 

Prerequisites
-------------

You are going to need to have python installed for this. This should work for both python 2.7 and 3 (I recommend having
from at least version 3.6.0 but earlier versions should be fine).

If you don’t have python installed on your machine, I’d recommend installing it through the `anaconda distribution
<https://www.continuum.io/downloads>`_. Anaconda comes with a bunch of libraries pre-installed so it’s easier to start off.


Installation
------------

To install all you need to do is open up your terminal and type in:

::

    pip install hockey_scraper


NHL Usage
---------

Standard Scrape Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Scrape data on a season by season level:

::

    import hockey_scraper

    # Scrapes the 2015 & 2016 season with shifts and stores the data in a Csv file
    hockey_scraper.scrape_seasons([2015, 2016], True)

    # Scrapes the 2008 season without shifts and returns a dictionary containing the pbp Pandas DataFrame
    scraped_data = hockey_scraper.scrape_seasons([2008], False, data_format='Pandas')

Scrape a list of games:

::

    import hockey_scraper

    # Scrapes the first game of 2014, 2015, and 2016 seasons with shifts and stores the data in a Csv file
    hockey_scraper.scrape_games([2014020001, 2015020001, 2016020001], True)

    # Scrapes the first game of 2007, 2008, and 2009 seasons with shifts and returns a Dictionary with the Pandas DataFrames
    scraped_data = hockey_scraper.scrape_games([2007020001, 2008020001, 2009020001], True, data_format='Pandas')

Scrape all games in a given date range:

::

    import hockey_scraper

    # Scrapes all games between 2016-10-10 and 2016-10-20 without shifts and stores the data in a Csv file
    hockey_scraper.scrape_date_range('2016-10-10', '2016-10-20', False)

    # Scrapes all games between 2015-1-1 and 2015-1-15 without shifts and returns a Dictionary with the pbp Pandas DataFrame
    scraped_data = hockey_scraper.scrape_date_range('2015-1-1', '2015-1-15', False, data_format='Pandas')


The dictionary returned by setting the default argument "data_format" equal to "Pandas" is structured like:

::

    {
      # Both of these are always included
      'pbp': pbp_df,
      'errors': scraping_errors,

      # This is only included when the argument 'if_scrape_shifts' is set equal to True
      'shifts': shifts_df
    }


Scraped files can also be saved in a separate directory if wanted. This allows one to re-scrape games quicker as we
don't need to retrieve them. This is done by specifying the keyword argument 'docs_dir' equal to True to automatically
create, store, and look in the home directory. Or you can provide your own directory where you want everything to be
stored (it must exist beforehand).

::

    import hockey_scraper

    # Create or try to refer to a directory in the home repository
    # Will create a directory called 'hockey_scraper_data' in the home directory (if it doesn't exist)
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=True)

    # Path to the given directory
    USER_PATH = "/...."

    # Scrapes the 2015 & 2016 season with shifts and stores the data in a Csv file
    # Also includes a path for an existing directory for the scraped files to be placed in or retrieved from.
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=USER_PATH)

    # Once could chose to re-scrape previously saved files by making the keyword argument rescrape=True
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=USER_PATH, rescrape=True)


Schedule
~~~~~~~~

The schedule for any past or future games can be scraped as follows:

::

    import hockey_scraper

    # As oppossed to the other calls the default format is 'Pandas' which returns a DataFrame
    sched_df = hockey_scraper.scrape_schedule("2019-10-01", "2020-07-01")

The columns returned are: ['game_id', 'date', 'venue', 'home_team', 'away_team', 'start_time', 'home_score', 'away_score', 'status']


Live Scraping
~~~~~~~~~~~~~

Here is a simple example of a way to setup live scraping. I strongly suggest checking out
`this section <https://hockey-scraper.readthedocs.io/en/latest/live_scrape.html>`_ of the docs if you plan on using this.
::

   import hockey_scraper as hs


   def to_csv(game):
       """
       Store each game DataFrame in a file

       :param game: LiveGame object

       :return: None
       """

       # If the game:
       # 1. Started - We recorded at least one event
       # 2. Not in Intermission
       # 3. Not Over
       if game.is_ongoing():
           # Print the description of the last event
           print(game.game_id, "->", game.pbp_df.iloc[-1]['Description'])

           # Store in CSV files
           game.pbp_df.to_csv(f"../hockey_scraper_data/{game.game_id}_pbp.csv", sep=',')
           game.shifts_df.to_csv(f"../hockey_scraper_data/{game.game_id}_shifts.csv", sep=',')

   if __name__ == "__main__":
       # B4 we start set the directory to store the files
       # You don't have to do this but I recommend it
       hs.live_scrape.set_docs_dir("../hockey_scraper_data")

       # Scrape the info for all the games on 2018-11-15
       games = hs.ScrapeLiveGames("2018-11-15", if_scrape_shifts=True, pause=20)

       # While all the games aren't finished
       while not games.finished():
           # Update for all the games currently being played
           games.update_live_games(sleep_next=True)

           # Go through every LiveGame object and apply some function
           # You can of course do whatever you want here.
           for game in games.live_games:
               to_csv(game)



.. NWHL Usage
.. -------------

.. Scrape data on a season by season level:

.. ::

    import hockey_scraper

    # Scrapes the 2015 & 2016 season and stores the data in a Csv file
    hockey_scraper.nwhl.scrape_seasons([2015, 2016])

    # Scrapes the 2008 season and returns a Pandas DataFrame containing the pbp
    scraped_data = hockey_scraper.nwhl.scrape_seasons([2017], data_format='Pandas')

.. Scrape a list of games:

.. ::

    import hockey_scraper

    # Scrape some games and store the results in a Csv file
    # Also saves the scraped pages
    hockey_scraper.nwhl.scrape_games([14694271, 14814946, 14689491], docs_dir="...Path you specified")

.. Scrape all games in a given date range:

.. ::

    import hockey_scraper

    # Scrapes all games between 2016-10-10 and 2017-01-01 and returns a Pandas DataFrame containing the pbp
    hockey_scraper.nwhl.scrape_date_range('2016-10-10', '2017-01-01', data_format='pandas')


The full documentation can be found `here <http://hockey-scraper.readthedocs.io/en/latest/>`_.


Contact
-------

Please contact me for any issues or suggestions. For any bugs or anything related to the code please open an issue.
Otherwise you can email me at Harryshomer@gmail.com.

