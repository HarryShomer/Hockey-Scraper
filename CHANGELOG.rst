v1.2.6
------

  * Added test coverage for most modules using pytest
  * Refactored large portion of 'html_pbp.py' and corrected minor parser fixes in regards to penalties
  * Added the module 'save_pages.py' which allows one to saves scraped files
  * Added keyword arguments 'rescrape' and 'docs_dir' to the three main scraping functions. Specifying a valid directory
    using 'docs_dir' will make us check if a file was already scraped and saved before getting it from the source. It will
    also provide a location for us to save it if we don't have it yet. 'rescrape' only applies when a valid directory
    is provided with 'docs_dir'. Setting 'rescrape' equal to True will have us scrape the file from the source even if
    it's saved and save this new one. 