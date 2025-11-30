from export_parsed_data import export_data
from website import WebsiteInfo, parse_all
import json
import sys
import validators

def main() -> None:
    """Main function of the program where the individual methods are called.
    """
    url, sublinks_to_visit = _get_args()
    website_info: WebsiteInfo = parse_all(url, sublinks_to_visit)

    # website_info_json: str = json.dumps(
    #     website_info.to_dict(), indent=4, ensure_ascii=False
    # )
    # print(website_info_json)

    export_data(website_info)

def _get_args() -> tuple[str, int]:
    """Get the input arguments from the user. The program requires an URL
    and an optional integer for the maximum number of sublinks to visit.

    Returns:
        tuple[str, int]: The website URL and the maximum number of sublinks to visit
    """
    url_arg_index = 1
    sublinks_to_visit_arg_index = 2
    required_arg_count = 2
    max_arg_count = 3

    if len(sys.argv) < required_arg_count or len(sys.argv) > max_arg_count:
        raise ValueError("Wrong number of parameters. Usage: python main.py <website's URL to parse> <maximum number of subpages to visit (optional)>")
    if not validators.url(sys.argv[url_arg_index]):
        raise ValueError(f"Invalid URL: {sys.argv[url_arg_index]}. Example of a valid URL: https://www.example.com")
    if len(sys.argv) == max_arg_count:
        if not isinstance(int(sys.argv[sublinks_to_visit_arg_index]), int):
            raise TypeError("Invalid sublinks_to_visit type. Must be an integer")
        if int(sys.argv[sublinks_to_visit_arg_index]) < 1:
            raise ValueError("The maximum number of subpages to visit must be at least 1 or more")
    
    # If sublinks to visit argument was not provided, default to 0
    if (len(sys.argv) == max_arg_count):
        return sys.argv[url_arg_index], int(sys.argv[sublinks_to_visit_arg_index])
    return sys.argv[url_arg_index], 0

if __name__ == "__main__":
    main()
