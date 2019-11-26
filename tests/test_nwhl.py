import pandas as pd
import pytest

import hockey_scraper as hs
import hockey_scraper.nwhl.scrape_schedule as sc
import hockey_scraper.nwhl.game_pbp as gp

hs.shared.docs_dir = "/Users/harryshomer/hockey/hockey_scraper_data/"


url = "https://www.nwhl.zone/stats#/100/game/268087/play-by-play"
x = gp.scrape_page(url)
#x = gp.get_pbp(268087)

