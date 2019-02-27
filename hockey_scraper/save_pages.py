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
        if not os.path.isdir(os.path.join(file_info['dir'], '/'.join(['docs', str(file_info['season']), file_info['type']]))):
            os.mkdir(os.path.join(file_info['dir'], '/'.join(['docs', str(file_info['season']), file_info['type']])))

    return os.path.join(file_info['dir'],
                        '/'.join(['docs', str(file_info['season']), file_info['type'], file_info['name'] + ".txt"]))


def create_season_dirs(season):
    """
    Creates the infrastructure to hold all the scraped docs for a season
    
    :param season: given season
                        
    :return: None
    """
    os.chdir(os.path.join(os.getcwd(), "docs"))

    # Folder for season
    os.mkdir(str(season))
    os.chdir(str(season))

    # Create all sub-folders
    os.mkdir("html_pbp")
    os.mkdir("json_pbp")
    os.mkdir("espn_pbp")
    os.mkdir("html_shifts_home")
    os.mkdir("html_shifts_away")
    os.mkdir("json_shifts")
    os.mkdir("html_roster")
    os.mkdir("json_schedule")
    os.mkdir("espn_scoreboard")

    # Move back to the previous directory
    os.chdir('..')


def check_file_exists(file_info):
    """
    Checks if the file exists. Also check if structure for holding scraped file exists to. If not, it creates it. 

    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.

    :return: Boolean - True if it exists
    """
    # Create the docs subdir if it doesn't exist
    if not os.path.isdir(os.path.join(file_info['dir'], 'docs')):
        os.mkdir("docs")
        os.mkdir("csvs")

    # Check if the folder for the season for the given game was created yet...if not create it
    if not os.path.isdir(os.path.join(file_info['dir'], '/'.join(['docs', str(file_info['season'])]))):
        create_season_dirs(file_info['season'])

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


def save_page(page, file_info, docs_dir):
    """
    Save the page we just scraped.
    
    Note: It'll only get saved if the directory already exists!!!!!!. I'm not dealing with any fuck ups. That would 
    involve checking if it's even a valid path and creating it. Make sure you get it right. 

    :param page: File scraped
    :param file_info: Dictionary containing the info on the file. Includes the name, season, file type, and the dir
                      we want to deposit any data in.
    :param docs_dir: Directory specified - either none or a valid dir

    :return: None
    """
    if docs_dir and page is not None and page != '':
        with open(create_file_path(file_info), 'w') as file:
            file.write(page)
