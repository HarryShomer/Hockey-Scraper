v1.2.6
------

  * Added test coverage for most modules using pytest
  * Refactored large portion of 'html_pbp.py' and corrected minor parser fixes in regards to penalties
  * Added the module 'save_pages.py' which allows one to saves scraped files
  * Added keyword arguments 'rescrape' and 'docs_dir' to the three main scraping functions. Specifying a valid directory using 'docs_dir' will make us check if a file was already scraped and saved before getting it from the source. It will also provide a location for us to save it if we don't have it yet. 'rescrape' only applies when a valid directory is provided with 'docs_dir'. Setting 'rescrape' equal to True will have us scrape the file from the source even if it's saved and save this new one.

v1.2.7
------
  * Added functionality to easier scrape live games
  * Fixed user warnings

v1.3
----
  * Added functionality to scrape NWHL data

v1.31
-----
  * Added functionality to automatically create docs_dir
  * Added folder to store csv files

v1.33
-----
  * Fixed bug with nhl changing contents of eventTypeId
  * Updated ESPN scraping after they changed the layout of the pages

v1.34
-----
  * Reflected change in url for ESPN scoreboard
  * Deprecated NWHL usage due as pbp parser isn't applicable due to UI changes (new source unknown)

v1.35
-----
  * Added nhl.scrape_function.scrape_schedule function
  * Now chunk calls to the nhl schedule api
  * Fixed nhl shift json endpoint

v1.36
-----
  * Refactored and cleaned up code across modules
  * Added names to utils.shared.Names
  * Changed errors/warning to print red in the console

v1.37
-----
  * Now saves scraped pages in docs_dir as a GZIP
  * Only print full error summary when the number of games scraped is >= 25
