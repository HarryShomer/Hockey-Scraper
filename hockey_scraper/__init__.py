#from .nwhl import scrape_functions as nwhl
from .nhl.live_scrape import ScrapeLiveGames, LiveGame
from .nhl.scrape_functions import scrape_games, scrape_date_range, scrape_seasons
from .nhl import live_scrape
from .utils import shared
