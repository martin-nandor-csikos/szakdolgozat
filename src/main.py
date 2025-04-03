from website import WebsiteInfo, parse_all
import json
import sys


def main() -> None:
    """Main function of the program where the individual methods are called."""

    website_to_parse: str = sys.argv[1]
    number_of_sites_to_visit: int = int(sys.argv[2])

    website_info: WebsiteInfo = parse_all(website_to_parse, number_of_sites_to_visit)
    website_info_json: str = json.dumps(website_info.to_dict(), indent=4)
    print(website_info_json)


if __name__ == "__main__":
    main()
