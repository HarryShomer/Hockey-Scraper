"""Saves the scraped docs so you don't have to re-scrape them every time you want to parse the docs. 


\**** Don't mess with this unless you know what you're doing \****
"""
import os


def create_file_path(file_info):
    """
    Creates the file path for a given file
    
    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.
    
    :return: path 
    """
    # Shitty fix for when you already have it saved but don't have nwhl folders
    if 'nwhl' in file_info['type']:
        if not os.path.isdir(os.path.join(file_info['dir'], 'docs', str(file_info['season']), file_info['type'])):
            os.mkdir(os.path.join(file_info['dir'], 'docs', str(file_info['season']), file_info['type']))

    return os.path.join(file_info['dir'], 'docs', str(file_info['season']), file_info['type'], file_info['name'] + ".txt")


def create_season_dirs(file_info):
    """
    Creates the infrastructure to hold all the scraped docs for a season
    
    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.
                        
    :return: None
    """
    sub_folders = ["html_pbp", "json_pbp", "espn_pbp", "html_shifts_home", "html_shifts_away", 
                   "json_shifts", "html_roster", "json_schedule", "espn_scoreboard"]

    season_path = os.path.join(file_info['dir'], 'docs', str(file_info['season']))
    os.mkdir(season_path)

    for sub_f in sub_folders:
        os.mkdir(os.path.join(season_path, sub_f))


def check_file_exists(file_info):
    """
    Checks if the file exists. Also check if structure for holding scraped file exists to. If not, it creates it. 

    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.

    :return: Boolean - True if it exists
    """
    # Create the docs and csvs subdir if it doesn't exist
    if not os.path.isdir(os.path.join(file_info['dir'], 'docs')):
        os.mkdir(os.path.join(file_info['dir'], 'docs'))
    if not os.path.isdir(os.path.join(file_info['dir'], 'csvs')): 
        os.mkdir(os.path.join(file_info['dir'], 'csvs'))

    # Check if the folder for the season for the given game was created yet...if not create it
    if not os.path.isdir(os.path.join(file_info['dir'], 'docs', str(file_info['season']))):
        create_season_dirs(file_info)

    return os.path.isfile(create_file_path(file_info))


def get_page(file_info):
    """
    Get the file so we don't need to re-scrape 

    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.

    :return: Response or None
    """
    with open(create_file_path(file_info), 'r') as my_file:
        return my_file.read().replace('\n', '')


def save_page(page, file_info):
    """
    Save the page we just scraped.
    
    Note: It'll only get saved if the directory already exists!!!!!!. I'm not dealing with any fuck ups. That would 
    involve checking if it's even a valid path and creating it. Make sure you get it right. 

    :param page: File scraped
    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.

    :return: None
    """
    if file_info['dir'] and page is not None and page != '':
        with open(create_file_path(file_info), 'w') as file:
            file.write(page)
