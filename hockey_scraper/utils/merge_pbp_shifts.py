import pandas as pd


def label_priority(row):
    """
    Priority for sorting
    
    Courtesy of Matt Barlowe (pre-NHL days)
    
    :param row: given event
    
    :return: given priority for that event
    """
    if row.Event in ['TAKE', 'GIVE', 'MISS', 'HIT', 'SHOT', 'BLOCK']:
        return 1
    elif row.Event == "GOAL":
        return 2
    elif row.Event == "STOP":
        return 3
    elif row.Event == "PENL":
        return 4
    elif row.Event == "OFF":
        return 5
    elif row.Event == 'ON':
        return 6
    elif row.Event == 'FAC':
        return 7
    elif row.Event == "PEND":
        return 8
    else:
        return 0


def group_shifts_cols(shifts, type_group_cols):
    """
    Group into columns for players by some column subset

    :param shifts: DataFrame of shifts
    :param type_group_cols: Some columns -> Either for On or Off

    :return: Grouped DataFrame
    """
    # Group both by player and player id get a new columns with a list of the group
    # The "Player" and "Player_Id" column contain a list of the grouped up players/player_ids
    grouped_df_player = shifts.groupby(by=type_group_cols, as_index=False)['Player'].apply(list).reset_index()
    grouped_df_playerid = shifts.groupby(by=type_group_cols, as_index=False)['Player_Id'].apply(list).reset_index()

    # Rename from nothing to something
    grouped_df_player = grouped_df_player.rename(index=str, columns={0: 'player'})
    grouped_df_playerid = grouped_df_playerid.rename(index=str, columns={0: 'player_Id'})

    # Player and Player Id are done separately above bec. they wouldn't work together
    # So just did both and slid over the relevant columns here
    grouped_df_player['player_Id'] = grouped_df_playerid['player_Id']

    # Rename either Start or End to Seconds Elapsed
    grouped_df_player = grouped_df_player.rename(index=str, columns={type_group_cols[-1:][0]: "Seconds_Elapsed"})
    grouped_df_player['Event'] = 'ON' if type_group_cols[-1:][0] == "Start" else "OFF"

    return grouped_df_player


def group_shifts_type(shifts, player_cols, player_id_cols):
    """
    Groups rows by players getting "On" and players getting "Off"

    :param shifts: Shifts_df
    :param player_cols: Columns for players (see previous function)
    :param player_id_cols: Column for player ids' (see previous functions)

    :return: Shifts DataFrame grouped by players on and off every second
    """
    # To subset for On and Off shifts
    group_cols_start = ['Game_Id', 'Period', 'Team', 'Home_Team', 'Away_Team', 'Date', 'Start']
    group_cols_end = ['Game_Id', 'Period', 'Team', 'Home_Team', 'Away_Team', 'Date', 'End']

    # Group by two type of column list above and then combine the two
    # Now have rows for On and rows for Off
    grouped_df_on = group_shifts_cols(shifts, group_cols_start)
    grouped_df_off = group_shifts_cols(shifts, group_cols_end)
    grouped_df = grouped_df_on.append(grouped_df_off)

    # Convert the Column which contain a list to the appropriate columns for both player and player_id
    players = pd.DataFrame(grouped_df.player.values.tolist(), index=grouped_df.index).rename(
        columns=lambda x: 'Player{}'.format(x + 1))
    player_ids = pd.DataFrame(grouped_df.player_Id.values.tolist(), index=grouped_df.index).rename(
        columns=lambda x: 'Player{}_id'.format(x + 1))

    # There are sometimes more than 6 players coming on at a time...it's not my problem (it's rare enough)
    grouped_df[player_cols] = players[['Player1', 'Player2', 'Player3', 'Player4', 'Player5', 'Player6']]
    grouped_df[player_id_cols] = player_ids[['Player1_id', 'Player2_id', 'Player3_id', 'Player4_id', 'Player5_id', 'Player6_id']]

    # Not needed anymore since we converted to new columns
    grouped_df = grouped_df.drop(['player', 'player_Id'], axis=1)

    return grouped_df.reset_index(drop=True)


def group_shifts(games_df, shifts):
    """
    As of now the shifts are 1 player per row. This groups by team by type (on/off) by second. So at the beginning of 
    the game we'll have one row with 6 players coming on for the home team and the same row for the away team.

    :param games_df: DataFrame containing Game_Id, Home_Team, and Away_Team -> Shifts_df doesn't contains home/away
    :param shifts: DataFrame of Shifts

    :return: Grouped Shifts DataFrame
    """
    # Up to 6 players on and off any time
    player_cols = [''.join(['Player', str(num)]) for num in range(1, 7)]
    player_id_cols = [''.join(['Player', str(num), '_id']) for num in range(1, 7)]

    # Merge in Home/Away Teams
    shifts = pd.merge(shifts, games_df, on=['Game_Id'])

    # Groups into on and off shift rows
    grouped_df = group_shifts_type(shifts, player_cols, player_id_cols)

    # Separate home and away for the purpose of the player columns (read below for more info)
    grouped_df_home = grouped_df[grouped_df.Team == grouped_df.Home_Team]
    grouped_df_away = grouped_df[grouped_df.Team == grouped_df.Away_Team]

    # Rename Players columns into both home and away
    # As on now it's player1, player1_id...etc.
    # To merge into the pbp we need to append home and away for the appropriate players
    # So we separate them and rename them with a "home" for the home teams and "away" for away teams
    grouped_df_home = grouped_df_home.rename(index=str, columns={col: 'home' + col for col in player_cols})
    grouped_df_home = grouped_df_home.rename(index=str, columns={col: 'home' + col for col in player_id_cols})
    grouped_df_away = grouped_df_away.rename(index=str, columns={col: 'away' + col for col in player_cols})
    grouped_df_away = grouped_df_away.rename(index=str, columns={col: 'away' + col for col in player_id_cols})

    # Group home/away shifts at same time on the same line
    df = pd.merge(grouped_df_home, grouped_df_away, on=['Game_Id', 'Period', 'Date', 'Event', 'Seconds_Elapsed'], 
                  how="outer", sort=True)

    df = df.rename(index=str, columns={"Home_Team_x": "Home_Team", "Away_Team_x": "Away_Team"})

    return df.reset_index(drop=True)


def merge(pbp_df, shifts_df):
    """
    Merge the shifts_df into the pbp_df.

    :param pbp_df: Play by Play DataFrame
    :param shifts_df: Shift Tables DataFrame

    :return: Play by Play DataFrame with shift info embedded
    """
    # To get the final pbp columns in the "correct" order
    pbp_columns = pbp_df.columns

    shifts_df['Player_Id'] = shifts_df['Player_Id'].astype(int)

    # Get unique game_id -> teams pair for placing in Shifts_df
    pbp_unique = pbp_df.drop_duplicates(subset=['Game_Id', 'Home_Team', 'Away_Team'])[['Game_Id', 'Home_Team', 'Away_Team']]

    # Group up shifts that start/end at the same time
    new_shifts = group_shifts(pbp_unique, shifts_df)
    new_shifts = new_shifts.where((pd.notnull(new_shifts)), None)

    # Add in & order rows
    new_pbp = pbp_df.append(new_shifts).reset_index(drop=True)
    new_pbp['Priority'] = new_pbp.apply(label_priority, axis=1)
    new_pbp = new_pbp.sort_values(by=['Game_Id', 'Period', 'Seconds_Elapsed', 'Priority'])

    return new_pbp[pbp_columns]
