from globals.enums import DataRegion
from export_parsed_data import export_data
from linkedin_links import fetch_links
from website import WebsiteInfo, parse_all
import argparse
import validators

def main() -> None:
    """Main function of the program where the individual methods are called.
    """
    try:
        args = _get_args()
    except ValueError as e:
        print(f"Invalid argument: {e}")
        return

    # Parse the given website
    website_info: WebsiteInfo = parse_all(args.link, args.sublinks, args.region)

    # Export the parsed data to a CSV file
    if website_info.has_data():
        export_data(website_info)

    if args.profiles > 0:
        profile_links = fetch_links(args.company, args.profiles, args.region)

def _get_args() -> argparse.Namespace:
    """Get the input arguments from the user using argparse.
    
    Required arguments:
        --link: The website URL to parse
    
    Optional arguments:
        --company: Company name for LinkedIn search
        --sublinks: Maximum number of subpages to visit (default: 0)

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Parse a website for employee information and find their LinkedIn profiles based on the provided company name. " \
        "The program will parse for names, phone numbers, emails and addresses. " \
        "LinkedIn profiles can also be fetched based on the provided company name and the maximum number of profiles to fetch. " \
        "It's important to mention that the program may return less results than the given --profiles argument." \
    )
    parser.add_argument(
        '-l', '--link',
        required=True,
        type=str,
        help="Website URL to parse (required)"
    )
    parser.add_argument(
        '-r', '--region',
        required=True,
        type=str,
        help="The primary region for data to be found. Supported regions: United States (us), Britain (gb), Hungarian (hu) (required)"
    )
    parser.add_argument(
        '-s', '--sublinks',
        required=False,
        type=int,
        default=0,
        help="Maximum number of subpages to visit (default: 0, only the given URL will be parsed)"
    )
    parser.add_argument(
        '-p', '--profiles',
        required=False,
        type=int,
        default=0,
        help="Maximum number of LinkedIn profiles to fetch (default: 0, fetch no profiles, required if --company argument is set)"
    )
    parser.add_argument(
        '-c', '--company',
        type=str,
        default=None,
        help="Company name for LinkedIn search (default: None, required if --profiles argument is set)"
    )

    args = parser.parse_args()
    
    if not validators.url(args.link):
        raise ValueError(f"URL '{args.link}' is invalid. Example of a valid URL: 'https://www.company.com/subpage'")
    if args.sublinks < 0:
        raise ValueError("The maximum number of subpages to visit must be at least 0 or more")
    if args.sublinks > 200:
        raise ValueError("The maximum number of subpages to visit must be at most 200")
    if args.profiles < 0:
        raise ValueError("The maximum number of LinkedIn profiles to fetch must be at least 0 or more")
    if args.profiles > 0 and args.company is None:
        raise ValueError("Argument --profiles is set but --company isn't. Both arguments must be provided for LinkedIn profile fetching.")
    if args.profiles == 0 and args.company is not None:
        raise ValueError("Argument --company is set but --profiles isn't. Both arguments must be provided for LinkedIn profile fetching.")
    if args.profiles > 200:
        raise ValueError("The maximum number of LinkedIn profiles to fetch must be at most 200")
    if args.region.lower() not in [DataRegion.UNITED_STATES.value, DataRegion.GREAT_BRITAIN.value, DataRegion.HUNGARY.value]:
        raise ValueError("Unsupported region. Supported regions: United States (us), Great Britain (gb), Hungary (hu)")
    
    if args.region:
        match args.region.lower():
            case DataRegion.HUNGARY.value:
                args.region = DataRegion.HUNGARY
            case DataRegion.UNITED_STATES.value:
                args.region = DataRegion.UNITED_STATES
            case _:
                args.region = DataRegion.GREAT_BRITAIN

    return args

if __name__ == "__main__":
    main()
