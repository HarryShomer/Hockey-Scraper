.. image:: https://badge.fury.io/py/hockey-scraper.svg
   :target: https://badge.fury.io/py/hockey-scraper
.. image:: https://readthedocs.org/projects/hockey-scraper/badge/?version=latest
   :target: https://readthedocs.org/projects/hockey-scraper/?badge=latest
   :alt: Documentation Status


Hockey-Scraper
==============

.. inclusion-marker-for-sphinx


**Note:**
 * Coordinates are only scraped from ESPN for versions 1.33+
 * NWHL usage has been deprecated due to the removal of the pbp information for each game.


Purpose
-------

Scrape NHL data off the NHL API and website. This includes the Play by Play and Shift data for each game. One can also scrape the schedule information. It currently supports all preseason, regular season, and playoff games from the 2007-2008 season onwards. 

Prerequisites
-------------

You are going to need to have python installed for this. This should work for both python 2.7 and 3. I recommend having
from at least version 3.6.0 but earlier versions should be fine.

Installation
------------

To install all you need to do is open up your terminal and run:

::

    pip install hockey_scraper


NHL Usage
---------

The full documentation can be found `here <http://hockey-scraper.readthedocs.io/en/latest/>`_.

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

      # This is only included when the argument 'if_scrape_shifts' is set equal to True
      'shifts': shifts_df
    }


Schedule
~~~~~~~~

The schedule for any past or future games can be scraped as follows:

::

    import hockey_scraper

    # As oppossed to the other calls the default format is 'Pandas' which returns a DataFrame
    sched_df = hockey_scraper.scrape_schedule("2019-10-01", "2020-07-01")

The columns returned are: `['game_id', 'date', 'venue', 'home_team', 'away_team', 'start_time', 'home_score', 'away_score', 'status']`


Persistent Data
~~~~~~~~~~~~~~~

All files and API calls retrieved can also be saved in a separate directory if wanted. The advanatge of this is reducing the amount of time needed to re-scrape a game as we don't need to re-retrieve them. You can also later choose to parse the files yourself and glean any extra information not captured by this project.

This is done by specifying the keyword argument `docs_dir` equal to `True` to automatically store and look for the data in a directory called `~/hockey_scraper_data`. Or you can provide your own directory where you want everything to be stored (it must exist beforehand). If no value is specified for `docs_dir` it will retrieve everything from the source and not from your saved directory.

For example, let's say we are want to have the JSON PBP data for game `2019020001 <http://statsapi.web.nhl.com/api/v1/game/2019020001/feed/live>`_. If an argument is passed for `docs_dir` it will first check to see if that call was already made by checking in the supplied directory. If it was, it will simply load in the data from that file and not make a GET request to the NHL API. However if it doesn' exist, it will make a GET request and then save the output to our directory. This will ensure that next time you are requesting that data it can load it from a file.

Here are some examples.

Default saving location in `~/hockey_scraper_data`


::

    # Create or try to refer to a directory in the home directory
    # Will create a directory called 'hockey_scraper_data' in the home directory (if it doesn't exist)
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=True)


User defined directory

::

    USER_PATH = "/...."
    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=USER_PATH)


You can override the existing files by specifying `rescrape=True`. It will retrieve all the files from source and save the newer versions to `docs_dir`.

::

    hockey_scraper.scrape_seasons([2015, 2016], True, docs_dir=USER_PATH, rescrape=True)



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



Contact
-------

Please contact me for any issues or suggestions. For any bugs or anything related to the code please open an issue.
Otherwise you can email me at Harryshomer@gmail.com.

