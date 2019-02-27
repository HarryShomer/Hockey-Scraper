NWHL Scraping Functions
=======================

Scraping
--------

There are three ways to scrape games:

\1. *Scrape by Season*:

Scrape games on a season by season level (Note: A given season is referred to by the first of the two years it spans.
So you would refer to the 2016-2017 season as 2016).
::

   import hockey_scraper

    # Scrapes the 2015 & 2016 season and stores the data in a Csv file (both are equivalent!!!)
    hockey_scraper.nwhl.scrape_seasons([2015, 2016])
    hockey_scraper.nwhl.scrape_seasons([2015, 2016], data_format='Csv')

    # Scrapes the 2008 season and returns a Pandas DataFrame
    scraped_data = hockey_scraper.nwhl.scrape_seasons([2017], data_format='Pandas')


\2. *Scrape by Game*:

Scrape a list of games provided.
::

    import hockey_scraper

    # Scrapes games and store in a Csv file
    hockey_scraper.nwhl.scrape_games([14694271, 14814946, 14689491], True)

    # Scrapes games and return DataFrame with data
    scraped_data = hockey_scraper.nwhl.scrape_games([14689624, 18507470, 20575219, 22207005], data_format='Pandas')

\3. *Scrape by Date Range*:

Scrape all games between a specified date range. All dates must be written in a "yyyy-mm-dd" format.
::

    import hockey_scraper

    # Scrapes all games between 2016-10-10 and 2017-01-01 and returns a Pandas DataFrame containing the pbp
    hockey_scraper.nwhl.scrape_date_range('2016-10-10', '2017-01-01', data_format='pandas')


Scrape Functions
~~~~~~~~~~~~~~~~
.. automodule:: hockey_scraper.scrape_functions_nwhl
   :members:

Html Schedule
~~~~~~~~~~~~~
.. automodule:: hockey_scraper.html_schedule_nwhl
   :members:

Json PBP
~~~~~~~~
.. automodule:: hockey_scraper.json_pbp_nwhl
   :members: