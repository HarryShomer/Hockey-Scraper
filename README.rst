.. image:: https://badge.fury.io/py/hockey-scraper.svg
   :target: https://badge.fury.io/py/hockey-scraper
.. image:: https://readthedocs.org/projects/hockey-scraper/badge/?version=latest
   :target: https://readthedocs.org/projects/hockey-scraper/?badge=latest
   :alt: Documentation Status


Hockey-Scraper
==============

.. inclusion-marker-for-sphinx


Purpose
-------

This package is designed to allow people to scrape the Play by Play and Shift data off of the National Hockey League
(NHL) API and website for all preseason, regular season, and playoff games since the 2007-2008 season.

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



Usage
-----

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
      # This is always included
      'pbp': pbp_df,

      # This is only included when the argument 'if_scrape_shifts' is set equal to True
      'shifts': shifts_df
    }


The full documentation can be found `here <http://hockey-scraper.readthedocs.io/en/latest/>`_.


Contact
-------

Please contact me for any issues or suggestions. For any bugs or anything related to the code please open an issue.
Otherwise you can email me at Harryshomer@gmail.com.









