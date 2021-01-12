"""
Interface for running cli commands
"""
import sys
import argparse
from .utils.shared import print_error
from .nhl.scrape_functions import scrape_games, scrape_date_range, scrape_seasons, scrape_schedule


def validate_args(user_args):
    """
    Validate that the passed args are sufficient enough to call the corresponding scraping function.
    Detailed checks are done later by the packcage after the specific function is called.

    :param user_args: ArgumentParser object

    :return: Boolean indicating if args are good
    """
    if user_args.reportType.lower() not in ['game', 'schedule']:
        print_error("Invalid parameter passed for -t/--reportType. Must be either `game` or `schedule`")
        return False

    # One of 3 not empty
    if not any([user_args.dateRange, user_args.seasons, user_args.games]):
        print_error("Must supply one of the following args: -d/--dateRange, -g/--games, or -s/--seasons. You passed none.")
        return False  

    # Date range - should only pass two
    # Whether or not they are valid is assessed later after calling one of the functions
    if user_args.dateRange and len(user_args.dateRange) != 2:
        print_error("Only 2 parameters should be passed for -d/--dateRange. You passed {}.".format(len(user_args.dateRange)))
        return False

    ### Everything else should be handled by just calling the functions
    return True


def run_cmd(user_args):
    """
    Run the appropriate command. Args already validated by this point.

    :param user_args: ArgumentParser object

    :return: None
    """
    if user_args.reportType.lower() == 'schedule': 
        scrape_schedule(user_args.dateRange[0], user_args.dateRange[1], rescrape=user_args.rescrape, docs_dir=user_args.fileDir, data_format='csv')
    else:
        if user_args.dateRange:
            scrape_date_range(user_args.dateRange[0], user_args.dateRange[1], user_args.shifts, 
                              docs_dir=user_args.fileDir, rescrape=user_args.rescrape, preseason=user_args.preseason)
        elif user_args.seasons:
            scrape_seasons(user_args.seasons, user_args.shifts, docs_dir=user_args.fileDir, rescrape=user_args.rescrape, preseason=user_args.preseason)
        else:
            scrape_games(user_args.games, user_args.shifts, docs_dir=user_args.fileDir, rescrape=user_args.rescrape)

    

def main():
    parser = argparse.ArgumentParser(description='CLI tool for the hockey_scraper project')

    ### Default to scraping games without shifts
    parser.add_argument('-t', "--reportType", help='Type of report to scrape. Either game or schedule.', default='game', type=str, required=False)  
    parser.add_argument("--shifts", help='Whether to include shifts.', action='store_true', default=False, required=False)

    ### Must pass one of these
    parser.add_argument('-d', "--dateRange", help='Date range to scrape between.', nargs='+', type=str, required=False, default=[])
    parser.add_argument('-s', "--seasons", help='Seasons to scrape.', nargs='+', type=int, required=False, default=[])
    parser.add_argument('-g', "--games", help='Game IDs to scrape.', nargs='+', type=str, required=False, default=[])

    ### Additonal optional args
    parser.add_argument('-f', "--fileDir", 
                        help='''Whether to store scraped files. If the flag is specified and no argument is passed, a directory is created in the root.
                                If an argument is passed with the flag the files are stored there (assuming the directory exists).
                             ''', 
                        default=None, type=str, required=False)

    parser.add_argument("-r", "--rescrape", help='Whether to re-scrape pages already scraped and stored in --fileDir.', 
                        action='store_true', default=False, required=False)

    parser.add_argument("-p", "--preseason", help='Whether to scrape preseason data.', action='store_true', default=False, required=False)

    args = parser.parse_args()

    if validate_args(args):
        run_cmd(args)



if __name__ == "__main__":
    main()
