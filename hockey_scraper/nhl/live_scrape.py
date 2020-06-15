"""
Module to scrape live game info
"""
import datetime
import time
import warnings
import pandas as pd
import hockey_scraper.nhl.game_scraper as game_scraper
import hockey_scraper.nhl.json_schedule as json_schedule
import hockey_scraper.nhl.pbp.espn_pbp as espn_pbp
import hockey_scraper.nhl.pbp.json_pbp as json_pbp
import hockey_scraper.nhl.playing_roster as playing_roster
import hockey_scraper.utils.shared as shared


def set_docs_dir(user_dir):
    """
    Set the docs directory
    
    :param user_dir: User specified directory for storing saves scraped files
    
    :return: None
    """
    # We always want to rescrape since the files are being updated constantly
    shared.if_rescrape(True)
    shared.add_dir(user_dir)


def check_date_format(date):
    """
    Verify the date format. If wrong raises a ValueError

    :param date: User supplied date

    :return: None
    """
    try:
        time.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Error: Incorrect format given for dates. They must be given like 'yyyy-mm-dd' "
                         "(ex: '2016-10-01').")


# TODO: Should I denote more member variables as private?
class LiveGame:
    """ 
    This is a class holds all the information for a given game
      
    :param int game_id: The NHL game id (ex: 2018020001)
    :param datetime start_time: The UTC time of when the game begins
    :param str home_team: Tricode for the home team (ex: NYR)
    :param str away_team: Tricode for the home team (ex: MTL)
    :param int espn_id: The ESPN game id for their feed
    :param str date: Date of the game (ex: 2018-10-30)
    :param bool if_scrape_shifts: Whether or not you want to scrape shifts
    :param str api_game_status: Current Status of the game - ["Final", "Live", "Intermission]
    :param str html_game_status: Current Status of the game - ["Final", "Live", "Intermission"]
    :param int intermission_time_remaining: Time remaining in the intermission. 0 if not in intermission
    :param dict players: Player info for both teams
    :param dict head_coaches: Head coaches for both teams
    :param DataFrame _pbp_df: Holds most recent pbp data
    :param DataFrame _shifts_df: Holds most recent shift data
    :param DataFrame _prev_pbp_df: Holds the previous pbp data (for just in case)
    :param DataFrame _prev_shifts_df: Holds the previous shift data (for just in case)
    """

    def __init__(self, game_id, start_time, home_team, away_team, status, espn_id, date, if_scrape_shifts):
        """ Constructor """
        # Given upon creation
        self.game_id = game_id
        self.start_time = start_time
        self.home_team = home_team
        self.away_team = away_team
        self.espn_id = espn_id
        self.date = date
        self.if_scrape_shifts = if_scrape_shifts

        # Html pbp is behind the json (json updates faster)
        self.api_game_status = status
        self.html_game_status = "Live"
        self.prev_api_game_status = status
        self.prev_html_game_status = "Live"
        self.intermission_time_remaining = 0

        # We know nothing to start off
        self.players = None
        self.head_coaches = None

        # Pbp and shift data - Will be filled in later
        # Also hold previous pair for checking for changes
        self._pbp_df = pd.DataFrame()
        self._shifts_df = pd.DataFrame()
        self._prev_pbp_df = pd.DataFrame()
        self._prev_shifts_df = pd.DataFrame()

        # Object creation message
        print("The LiveGame object for game {game_id} has been created. ".format(game_id=game_id), end="")
        if self.time_until_game() <= 0:
            print("The game has started.")
        else:
            print("The game starts in {time} seconds.".format(time=self.time_until_game()))


    @property
    def pbp_df(self):
        if isinstance(self._pbp_df, pd.DataFrame):
            return self._pbp_df
        else:
            return pd.DataFrame()

    @property
    def shifts_df(self):
        if isinstance(self._shifts_df, pd.DataFrame):
            return self._shifts_df
        else:
            return pd.DataFrame()

    @property
    def prev_pbp_df(self):
        if isinstance(self._prev_pbp_df, pd.DataFrame):
            return self._prev_pbp_df
        else:
            return pd.DataFrame()

    @property
    def prev_pbp_df(self):
        if isinstance(self._prev_shifts_df, pd.DataFrame):
            return self._prev_shifts_df
        else:
            return pd.DataFrame()


    def scrape(self, force=False):
        """
        Scrape the given game. Check if currently ongoing or started
        
        :param bool force: Whether or not to force it to scrape even if it's over
        
        :return: None
        """
        # 1. force = False: If the game hasn't eclipsed the starting time or is over we don't scrape
        # 2. force = True: We always scrape
        if (self.time_until_game() == 0 and not self.is_game_over(prev=True)) or force:
            self.scrape_live_game(force=force)


    def scrape_live_game(self, force=False):
        """
        Scrape the live info for a given game
        
        :param force: Whether to scrape no matter what (used for intermission here)
        
        :return: None
        """
        game_json = json_pbp.get_pbp(str(self.game_id))

        # When don't have json...can't do anything without it
        if game_json is None:
            return

        # Shift Game Statuses b4 we do anything
        self.prev_api_game_status = self.api_game_status
        self.prev_html_game_status = self.html_game_status

        # Swap old pbp & shift DataFrames
        self._prev_pbp_df = self._pbp_df
        self._prev_shifts_df = self._shifts_df

        # If json is in intermission:
        # Update self.api_game_status, get minutes remaining in intermission, and check if html is intermission too.
        # If both feeds are in intermission we return, otherwise we wait for the html to catch up.
        # "Intermission" is my own game status so otherwise just take whatever is in the api
        if game_json['liveData']['linescore']['intermissionInfo']['inIntermission']:
            self.api_game_status = "Intermission"
            self.intermission_time_remaining = game_json['liveData']['linescore']['intermissionInfo']["intermissionTimeRemaining"]

            # If see the both says intermission and we do too, we can just safely return and not bother with scraping.
            # This will be false if the HTML hasn't updated yet to intermission
            # If force we scrape no matter what
            if self.is_intermission() and not force:
                return
        else:
            # Update API Status if NOT in intermission to whatever is there
            self.api_game_status = game_json["gameData"]["status"]["abstractGameState"]

        # Leave if b4 game started
        if game_json["gameData"]["status"]["abstractGameState"] in ["Preview"]:
            self.html_game_status = self.api_game_status = game_json["gameData"]["status"]["abstractGameState"]
            return

        # We get this the 1st time it scrapes the info (or when it's first available)
        # Don't bother with earlier as it may not be there or we may end up with an old version
        if not self.players:
            roster = playing_roster.scrape_roster(self.game_id)
            if roster is not None:
                self.players, _ = game_scraper.get_teams_and_players(game_json, roster, self.game_id)
                self.head_coaches = roster['head_coaches']
            else:
                return  # If we try and still can't get it we leave - Termination Reason #2

        # Don't bother with scraper warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # pay attention to each argument
            self._pbp_df, self.html_game_status = game_scraper.scrape_pbp_live(self.game_id, self.date,
                                                                              {"head_coaches": self.head_coaches},
                                                                              game_json, self.players,
                                                                              {"Home": self.home_team, "Away": self.away_team},
                                                                              espn_id=self.espn_id)
            if self.if_scrape_shifts:
                self._shifts_df = game_scraper.scrape_shifts(self.game_id, self.players, self.date)


    def is_ongoing(self):
        """
        Check if the game is currently being played. 
        
        The logic here is that we run into an issue with intermission and the end of game. If the game is just changed 
        to Final or Intermission the end user will assume the game isn't ongoing and will not update with the most
        recent events. They'll be delayed for intermission and won't place it at all for Final games. So we use the 
        previous event as a guide. If it's currently in intermission or Final - we check the previous status. If it's 
        the same the user already has the data. Otherwise we 'lie' and say the game is still ongoing.
        
        :return: Boolean
        """
        # The game is currently being played
        if self.time_until_game() == 0 and not self.is_game_over() and not self.is_intermission() and self.pbp_df.shape[0] > 0:
            return True
        # Since it's not being played check if game is over and if it wasn't for the previous
        elif self.is_game_over() and not self.is_game_over(prev=True):
            return True
        # Check if it's in intermission and the if it was for the previous event
        elif self.is_intermission() and not self.is_intermission(prev=True):
            return True
        else:
            return False


    def time_until_game(self):
        """
        Return the seconds until the game starts

        :return: seconds until game 
        """
        delta = self.start_time - datetime.datetime.utcnow()
        if delta.days >= 0:
            return delta.seconds
        else:
            return 0


    def is_game_over(self, prev=False):
        """
        Check if the game is over for both the html and json pbp. If prev=True check for the previous event
        
        :param prev: Check the game status for the previous event
        
        :return: Boolean - True if over
        """
        if not prev:
            return self.html_game_status == self.api_game_status == "Final"
        else:
            return self.prev_html_game_status == self.prev_api_game_status == "Final"


    def is_intermission(self, prev=False):
        """
        Check if in intermission for both the html and json pbp. If prev=True check for the previous event
        
        :param prev: Check the game status for the previous event

        :return: Boolean - True if yes
        """
        if not prev:
            return self.html_game_status == self.api_game_status == "Intermission"
        else:
            return self.prev_html_game_status == self.prev_api_game_status == "Intermission"



class ScrapeLiveGames:
    """
    Class than contains the info for all the games on a specific day
    
    :param str date: Date of games (ex: 2018-10-30)
    :param bool preseason: If you want to scrape preseason games
    :param bool if_scrape_shifts: Whether or not you want to scrape shifts
    :param list live_games: List of LiveGame objects for 
    :param int pause: Amount to pause after each scraping call
    """

    def __init__(self, date, preseason=False, if_scrape_shifts=False, pause=15, game_ids=list()):
        """
        Initialize the ScrapeLiveGames object with games for the day
        
        :param date: Date 
        :param preseason: If scrape preseason
        :param if_scrape_shifts: Whether to scrape the shifts
        :param pause: time to pause
        :param game_ids: If only want specific games
        """
        # First check date
        check_date_format(date)

        self.user_game_ids = game_ids
        self.date = date
        self.preseason = preseason
        self.if_scrape_shifts = if_scrape_shifts
        self.live_games = self.get_games()          # Hold list of LiveGame objects for that day
        self.pause = pause


    def get_games(self):
        """
        Get initial game info -> Called with object creation. Includes: players, espn_ids, standard game info
        
        :return: Dict - LiveGame objects for all games today
        """
        game_objs = []

        # Get the initial schedule & espn game ids just in case
        games = json_schedule.scrape_schedule(self.date, self.date, not_over=True, preseason=self.preseason)
        games = self.get_espn_ids(games)

        # Only keep the games we want if the user specified games
        if self.user_game_ids:
            games = [game for game in games if game['game_id'] in self.user_game_ids]

        # Get rosters for each game
        for game in games:
            game_objs.append(LiveGame(game['game_id'], game['start_time'], game['home_team'], game['away_team'],
                                      game['status'], game['espn_id'], self.date, self.if_scrape_shifts))

        return game_objs


    def get_espn_ids(self, games):
        """
        Get espn game ids for all games that day

        :param list games: games today

        :return: Games with corresponding espn game ids
        """
        # Get all espn info
        response = espn_pbp.get_espn_date(self.date)
        game_ids = espn_pbp.get_game_ids(response)
        espn_games = espn_pbp.get_teams(response)

        # Match up
        for i in range(len(games)):
            for j in range(len(espn_games)):
                if games[i]['home_team'] in espn_games[j] or games[i]['away_team'] in espn_games[j]:
                    games[i]['espn_id'] = game_ids[j]

        return games


    def update_live_games(self, force=False, sleep_next=False):
        """
        Scrape the pbp & shifts of ongoing games
        
        :param bool force: Whether or not to force it to scrape even if it's in intermission
        :param bool sleep_next: Sleep until the next game starts
        
        :return: None
        """
        # Check if we need to sleep
        if sleep_next:
            self.sleep_next_game()

        for game in self.live_games:
            game.scrape(force=force)

        time.sleep(self.pause)


    def sleep_next_game(self):
        """
        Sleep until the next game starts. Otherwise just looping and doing nothing
        
        :return: None
        """
        # Get rid of final games...we are looking at current or upcoming games
        non_final_games = [game for game in self.live_games if not game.is_game_over()]

        # Lets get all the games NOT ongoing but aren't over (so scheduled games)
        scheduled_games = [game for game in non_final_games if game.time_until_game() > 0]

        # If all the non-final games haven't started yet let's find the next game
        # Get earliest in the bunch
        if len(scheduled_games) == len(non_final_games):
            min_game = min(scheduled_games, key=lambda x: x.time_until_game())

            if min_game.time_until_game() > 0:
                print("\nSleeping for {} seconds until the next earliest game starts.".format(min_game.time_until_game()))
                time.sleep(min_game.time_until_game())


    def finished(self):
        """
        Check if done with all games
        
        :return: Boolean
        """
        # Count finished games
        finished_games = 0
        for game in self.live_games:
            if game.is_game_over():
                finished_games += 1

        # If the # of finished games == # of total games
        return len(self.live_games) == finished_games

