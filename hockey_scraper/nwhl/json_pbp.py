"""
Scrape the PBP info for a given game
"""
import datetime
import json
import pandas as pd
import hockey_scraper.utils.shared as shared


def get_pbp(game_id):
    """
    Get the response for a game (e.g. https://www.nwhl.zone/game/get_play_by_plays?id=18507472)
    
    :param game_id: Given Game id (e.g. 18507472)
    
    :return: Json
    """
    page_info = {
        "url": 'https://www.nwhl.zone/game/get_play_by_plays?id={}'.format(game_id),
        "name": str(game_id),
        "type": "nwhl_json_pbp",
        "season": "nwhl",
    }
    response = shared.get_file(page_info)

    if not response:
        print("Json pbp for game {} is either not there or can't be obtained".format(game_id))
        return {}
    else:
        return json.loads(response)


def get_roster(game_json):
    """
    Parse the roster info in the game json
    
    :param game_json: Json of all the info for a game
    
    :return: Dict: Key = Player id, Value = Name
    """
    players = {}
    for player in game_json['roster_player']:
        players[player['id']] = " ".join([player['first_name'].strip(), player['last_name'].strip()])

    return players


def get_goal_players(play, event, players):
    """
    Get all the players on ice for a goal (modify play object)
    
    :param play: Our play info
    :param event: PBP play info
    :param players: Player id -> Name conversion
    
    :return: None
    """
    # Which team is plus/minus
    if play['ev_team'] == play['home_team']:
        ptype_team = {'plus': "home", 'minus': "away"}
    else:
        ptype_team = {'plus': "away", 'minus': "home"}

    # Plus and minus players
    for ptype in ['plus', 'minus']:
        for num in range(1, 7):
            play['{}Player{}_id'.format(ptype_team[ptype], num)] = event['play_actions'][1].get("{}_player_{}".format(ptype, num))

            # Control for None
            if play['{}Player{}_id'.format(ptype_team[ptype], num)]:
                play['{}Player{}'.format(ptype_team[ptype], num)] = players.get(int(play['{}Player{}_id'.format(ptype_team[ptype], num)]))
            else:
                play['{}Player{}'.format(ptype_team[ptype], num)] = None


def parse_event(event, score, teams, date, game_id, players):
    """
    Parses a single event when the info is in a json format

    :param event: json of event 
    :param score: Current score of the game
    :param teams: Teams dict (id -> name)
    :param date: date of the game
    :param game_id: game id for game
    :param players: Dict of player ids to player names
    
    :return: dictionary with the info
    """
    play = dict()

    # Basic shit
    play['play_index'] = event['play_index']
    play['date'] = date
    play['game_id'] = game_id
    play['season'] = shared.get_season(date)
    play['period'] = event['time_interval']
    play['seconds_elapsed'] = shared.convert_to_seconds(event['clock_time_string']) if event['clock_time_string'] else None
    play['home_score'], play['away_score'] = score['home'], score['away']

    # If shootout go with 'play_by_play_string' field -> more descriptive
    play['event'] = event['play_type'] if event['play_type'] != "Shootout" else event['play_by_play_string'].strip()

    # Teams
    play['home_team'], play['away_team'] = teams['home']['name'], teams['away']['name']
    if event['play_summary']['off_team_id'] == teams['home']['id']:
        play['ev_team'] = teams['home']['name']
    else:
        play['ev_team'] = teams['away']['name']

    # Player Id
    play['p1_id'] = event.get('primary_player_id')
    play['away_goalie_id'] = event['play_actions'][0].get('away_team_goalie')
    play['home_goalie_id'] = event['play_actions'][0].get('home_team_goalie')

    play['away_goalie'] = players.get(int(play['away_goalie_id']) if play['away_goalie_id'] not in ['', None] else 0)
    play['home_goalie'] = players.get(int(play['home_goalie_id']) if play['home_goalie_id'] not in ['', None] else 0)

    # Event specific stuff
    if event['play_type'] == 'Faceoff':
        play['p2_id'] = event['play_summary'].get("loser_id")
    elif event['play_type'] == 'Penalty':
        # TODO: Format better?
        play['details'] = ",".join([str(event['play_summary'].get("infraction_type", " ")),
                                    str(event['play_summary'].get("penalty_type", " ")),
                                    str(event['play_summary'].get("penalty_minutes", " "))])
    elif event['play_type'] == "Goal":
        get_goal_players(play, event, players)
        play['p2_id'] = event['play_summary'].get("assist_1_id")
        play['p3_id'] = event['play_summary'].get("assist_2_id")

        # Update Score
        if event['play_summary']['off_team_id'] == teams['home']['id']:
            score['home'] += 1
        else:
            score['away'] += 1

    # Player Id's --> Player Names
    for num in range(1, 4):
        player_id = play.get('p{num}_id'.format(num=num), 0)
        # Control for None
        player_id = player_id if player_id else 0
        play['p{num}_name'.format(num=num)] = players.get(int(player_id))

    # Coords
    play['xC'] = event['play_summary'].get('x_coord')
    play['yC'] = event['play_summary'].get('y_coord')

    return play


def parse_json(game_json, game_id,):
    """
    Scrape the json for a game
    
    plus, minus players

    :param game_json: raw json
    :param game_id: game id for game

    :return: Either a DataFrame with info for the game 
    """
    cols = ['game_id', 'date', 'season', 'period', 'seconds_elapsed', 'event', 'ev_team', 'home_team', 'away_team',
            'p1_name', 'p1_id', 'p2_name', 'p2_id', 'p3_name', 'p3_id',
            "homePlayer1", "homePlayer1_id", "homePlayer2", "homePlayer2_id", "homePlayer3", "homePlayer3_id",
            "homePlayer4", "homePlayer4_id", "homePlayer5", "homePlayer5_id", "homePlayer6", "homePlayer6_id",
            "awayPlayer1", "awayPlayer1_id", "awayPlayer2", "awayPlayer2_id", "awayPlayer3", "awayPlayer3_id",
            "awayPlayer4", "awayPlayer4_id", "awayPlayer5", "awayPlayer5_id", "awayPlayer6", "awayPlayer6_id",
            'home_goalie', 'home_goalie_id', 'away_goalie', 'away_goalie_id', 'details', 'home_score', 'away_score',
            'xC', 'yC', 'play_index']

    # B4 anything - if there are no plays we leave
    if len(game_json['plays']) == 0:
        shared.print_warning("The Json pbp for game {} contains no plays and therefore can't be parsed".format(game_id))
        return pd.DataFrame()

    # Get all the players in the game
    players = get_roster(game_json)

    # Initialize & Update as we go along
    score = {"home": 0, "away": 0}
    teams = {"home": {"id": game_json['game']['home_team'], "name": game_json['team_instance'][0]['abbrev']},
             "away": {"id": game_json['game']['away_team'], "name": game_json['team_instance'][1]['abbrev']}
             }

    # Get date from UTC timestamp
    date = game_json['plays'][0]['created_at']
    date = datetime.datetime.strptime(date[:date.rfind("-")], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

    try:
        events = [parse_event(play, score, teams, date, game_id, players) for play in game_json['plays']]
    except Exception as e:
        shared.print_warning('Error parsing Json pbp for game {} {}'.format(game_id, e))
        return pd.DataFrame()

    df = pd.DataFrame(events, columns=cols)

    # Get rid of null events and order by play index
    df = df[(~pd.isnull(df['event'])) & (df['event'] != "")]
    df = df.sort_values(by=['play_index'])
    df = df.drop(['play_index'], axis=1)

    return df.reset_index(drop=True)


def scrape_pbp(game_id):
    """
    Scrape the pbp data for a given game
    
    :param game_id: Given Game id (e.g. 18507472)
    
    :return: DataFrame with pbp info
    """
    game_json = get_pbp(game_id)

    if not game_json:
        shared.print_warning("Json pbp for game {} is not either not there or can't be obtained".format(game_id))
        return pd.DataFrame()

    try:
        game_df = parse_json(game_json, game_id)
    except Exception as e:
        shared.print_warning('Error parsing Json pbp for game {} {}'.format(game_id, e))
        return pd.DataFrame()

    return game_df

