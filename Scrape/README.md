# Hockey Scraper

This project is designed to allow people to scrape Play by Play and Shift data off of the 
National Hockey League (NHL) API and website for all regular season and playoff games
since the 2010-2011 season (further testing needs to be done to ensure it works for earlier
seasons.  


## Prerequisites

You are going to need to have python installed for this. Specifically, you'll need from
at least version 3.6.0.

If you don't have python installed on your machine, I'd recommend installing it through
the anaconda distribution (here - https://www.continuum.io/downloads). Anaconda comes 
with a bunch of libraries pre-installed so it'll be easier to start off. 


## How to Use

First just download this folder onto your computer.

Then open up the command line or terminal and navigate over to where the folder is placed
on your computer. For example let's say that the folder is placed in a directory called
'Hockey', you would then (on a mac) open up your terminal and type: 

```
cd /Users/Username/Hockey/Scrape
``` 

Then type in "python" to open the interactive python console. 

You then want to import the file in the folder which contains the functions for scraping
the data. So just type in (and press enter): 

```
import scrape_functions  
```

The function "scrape" (found, of course, in the scrape_functions file) is used to scrape 
data on a season by season level. It takes two arguments (by default the play-by-play is 
scraped, you need to specify whether or not you want to scrape the shifts):

1. seasons - List of seasons you want to scrape (Note: A given season is referred to by
the first of the two years it spans. So you would refer to the 2016-2017 season as 2016.

2. if_shifts - Boolean indicating whether or not you want to scrape the shifts too 


So let's say you want to get the play by play and shift data from the 2015-2016 and 
2016-2017 season. Assuming you have migrated over to the folder, opened up python, and 
imported the scrape_functions file, you would type:

```
scrape_functions.scrape([2015, 2016], True) 
```

And that's it. When the program is done you will find two new files for each season on 
your computer (and in the same folder as your code):

1. nhl_pbp20162017.csv and nhl_pbp20152016.csv which contains the play by play info for
   each game each season.

2. nhl_shifts20162017.csv and nhl_shifts20152016.csv which contains the shift info for each
   game each season 
   

It's important to note add that this does take some time to run. A season of just play
by play data takes about ~2 hours to run and if you include shifts about ~2:30.  




