from export_parsed_data import export_data
# from linkedin_links import get_links
from website import WebsiteInfo, parse_all
import argparse
import validators

def main() -> None:
    """Main function of the program where the individual methods are called.
    """
    args = _get_args()

    # Parse the given website
    website_info: WebsiteInfo = parse_all(args.link, args.sublinks)

    # Find LinkedIn links for the found names
    if len(website_info.found_names) != 0:
        names_list = list(website_info.found_names.keys())
        # print(get_links(names_list, args.company))

    # Export the parsed data to a CSV file
    if website_info.has_data():
        export_data(website_info)

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
        "If names were found, the app will search for their LinkedIn profiles. "
    )
    parser.add_argument(
        '-c', '--company',
        required=True,
        type=str,
        default=None,
        help="Company name for LinkedIn search (required)"
    )
    parser.add_argument(
        '-l', '--link',
        required=True,
        type=str,
        help="Website URL to parse (required)"
    )
    parser.add_argument(
        '-s', '--sublinks',
        required=False,
        type=int,
        default=0,
        help="Maximum number of subpages to visit (default: 0, only the given URL will be parsed)"
    )

    args = parser.parse_args()
    
    if not validators.url(args.link):
        raise ValueError(f"Invalid URL: {args.link}. Example of a valid URL: https://www.company.com")
    if args.sublinks < 0:
        raise ValueError("The maximum number of subpages to visit must be at least 0 or more")
    return args

if __name__ == "__main__":
    main()
