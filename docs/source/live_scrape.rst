Live Scraping
=============

Standard Usage
--------------

To get all the info for every game on a specific day we create a ScrapeLiveGames object.
::

    import hockey_scraper as hs

    todays_games = hs.ScrapeLiveGames("2018-11-15", if_scrape_shifts=True, pause=15)


Once created this object will contain an attribute called 'live_games' that holds a list of LiveGame objects for that
day. LiveGame objects hold all the pertinent game information for each game. This includes the most recent
pbp and shift data for that game. Here are all the attributes for the LiveGame class:
::

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

Here's a simple example of scraping the games continuously for a single date. This will run until every game is finished:

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


In the above example, we set a directory to store the most recent version of every scraped file. We then grab the
initial game info for each game for that day. We decide we want to include shifts and to pause 15 seconds after updating
all the games. We then enter a loop that will be terminated once every game is finished. Once in the loop we first
scrape the new info for every game and then pause for the specified time (default is 15).

Once we process the new data we then, presumably, want to do something with it. Here, I decided to merely print the last
event in the game and store the newer data in files. We do this by iterating through each LiveGame object in the 'live_games'
attribute and calling the function 'to_csv'. In 'to_csv', before doing anything we check if the game is 'ongoing'.
This checks whether the game is either over or in intermission. If it is there isn't a whole lot to update. If it's
neither we print the last event and then store the data for both the pbp & shifts.

Another option we have is for the program to sleep until the first game starts. Unless you want to start this yourself
everyday, you'll probably be scheduling it to start at some time every day. This means from when you start the program
to when the first game starts may be a significant amount of time (fwiw, it will just loop and not scrape anything). But
you can set it to sleep until the first game is scheduled to start. This can be done by setting the keyword 'sleep_next'
to True. This check to see if the only games left are scheduled games yet to start. If so it sleeps until the next
earliest game starts.
::

   # Causes the program to sleep until the first game starts
   games.update_live_games(sleep_next=True)


You can also specify which games you want to scrape for that day (maybe you only care about one game), by setting the
keyword 'game_ids' equal to a list of NHL Game ID's of the games you want when instantiating a ScrapeLiveGame object. You
can of course to choose to filter it however you want as the list of LiveGame objects is a attribute of the object. Either
way I strongly suggest creating a ScrapeLiveGames object and then either extracting the game you want or filtering it
rather than instantiating a LiveGame object (you will be on the hook for a lot of information)
::

   # Only want those those two games.
   games = hs.ScrapeLiveGames("2018-11-15", if_scrape_shifts=True, pause=15, game_ids=[2018020280, 2018020281])


Further Usage
-------------

If you would like more control over what you are doing then you should be dealing directly with LiveGame objects. As
mentioned previously, still use ScrapeLiveGames to get the game info but you can then just extract the list of games
and do as you please.

Using the previous example here we are scraping each game individually:
::

   # Scrape the info for all the games on 2018-11-15
   games = hs.ScrapeLiveGames("2018-11-15", if_scrape_shifts=True, pause=15)

   while not games.finished():
       # Go through every LiveGame object
       for game in games.live_games:
           # Scrape each game individually
           game.scrape()

           # Apply some function to every game
           to_csv(game)

       # Pause after each scraping chunk
       time.sleep(15)

If you don't trust when I choose to not scrape (when the game is over or in intermission), you can make the keyword
'force' equal to True. This will re-scrape it as long as the game already started.
::

   game.scrape(force=True)

This will override everything and will attempt to scrape the game no matter what. This means you are have to be on top
of when to stop scraping the game. You are also on the hook for any potential errors.

You may also want to handle things like the start time of games yourself. As mentioned using ScrapeLiveGames we can
set 'sleep_next' equal to True to sleep until the next game starts if no game is going on. You can also use the keyword
'start_time' for a LiveGame object that will give you a datetime object with the scheduled starting time for a given
game in UTC time. Lastly, you can also use the function 'time_until_game()' that will return how many seconds until the
game starts.
::

   >>> games = hs.ScrapeLiveGames("2018-11-09", if_scrape_shifts=True, pause=15)
   >>> games.live_games[0].start_time
   datetime.datetime(2018, 11, 10, 0, 0)
   >>> games.live_games[0].time_until_game()
   64599

You can use this how you please. For example, you may want to create a separate thread for each game and have it sleep
until the game starts. Or maybe you want to use it another way. Either way it's there.

There are also a few methods that return the give information about the current status of the game. The first two return
whether the game is in intermission or whether it's over.
::

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

Two things probably stand out is the option to check the status for the previous event (why do we care what it was earlier?)
and the fact that two statuses exist.

First let's talk about the two status. There are currently two pages that always need to be scraped for for data for
the Play-By-Play. One is an html file and one is the json api. The issue is that the api updates faster than the html.
So the api may say the game is over but the html version is still missing a few events. For this reason we need to check
that both are aligned.

The 'prev' keyword for both comes into play when we consider the last method 'is_ongoing'. This checks whether the game
is currently being played. Which means the game: Started, is not in intermission, and is not over. Here's the method:
::

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

I recommend looking at the function definition written above. Basically checking the previous event makes sure we got
the most recent event if the game is over or in intermission. So if the last status was intermission and this one is
too we know we don't need to scrape. But if the last status wasn't the means we are missing some information (presumably
something happened between the last event and the end of the period).

Live Scrape
~~~~~~~~~~~
.. automodule:: hockey_scraper.nhl.live_scrape
   :members: