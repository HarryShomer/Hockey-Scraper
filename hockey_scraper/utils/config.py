"""
Basic configurations
"""

# Directory where to save pages
# When True assumes ~/hockey_scraper_data
# Otherwise can take str to `existing` directory
DOCS_DIR = False

# Boolean that tells us whether or not we should re-scrape a given page if it's already saved
RESCRAPE = False

# Whether to log verbose errors to log file
LOG = False