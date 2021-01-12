Command Line Interface
======================

There also exists a cli tool called `hockey-scraper` which can be used to pull data. Users may find this more convenient than using python directly for simple queries.

The usage for the tool can be found below: 

.. code-block:: console

    usage: hockey-scraper [-h] [-t REPORTTYPE] [--shifts] [-d DATERANGE [DATERANGE ...]] [-s SEASONS [SEASONS ...]]
                      [-g GAMES [GAMES ...]] [-f FILEDIR] [-r] [-p]

    CLI tool for the hockey_scraper project

    optional arguments:
      -h, --help            show this help message and exit
      -t REPORTTYPE, --reportType REPORTTYPE
                            Type of report to scrape. Either game or schedule.
      --shifts              Whether to include shifts.
      -d DATERANGE [DATERANGE ...], --dateRange DATERANGE [DATERANGE ...]
                            Date range to scrape between.
      -s SEASONS [SEASONS ...], --seasons SEASONS [SEASONS ...]
                            Seasons to scrape.
      -g GAMES [GAMES ...], --games GAMES [GAMES ...]
                            Game IDs to scrape.
      -f FILEDIR, --fileDir FILEDIR
                            Whether to store scraped files. If the flag is specified and no argument is passed, a directory is created
                            in the root. If an argument is passed with the flag the files are stored there (assuming the directory
                            exists).
      -r, --rescrape        Whether to re-scrape pages already scraped and stored in --fileDir.
      -p, --preseason       Whether to scrape preseason data.


CLI
~~~
.. automodule:: hockey_scraper.cli
   :members: