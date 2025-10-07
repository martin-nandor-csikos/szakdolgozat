from website import WebsiteInfo, parse_all
import json
import sys
import validators


def main() -> None:
    """Main function of the program where the individual methods are called."""

    if len(sys.argv) != 3:
        print("Wrong number of parameters. Usage: python main.py <website's URL to parse> <maximum number of subpages to visit (must be >=0)>")
        sys.exit(1)

    website_to_parse: str = sys.argv[1]
    try:
        assert validators.url(website_to_parse), f"Invalid URL: {website_to_parse}. Example of a valid URL: https://www.example.com"
    except AssertionError as e:
        print(e)
        sys.exit(1)

    number_of_sites_to_visit: int = int(sys.argv[2])
    if number_of_sites_to_visit < 0:
        print("The maximum number of subpages to visit must be at least 0 or more")
        sys.exit(1)

    website_info: WebsiteInfo = parse_all(website_to_parse, number_of_sites_to_visit)
    website_info_json: str = json.dumps(
        website_info.to_dict(), indent=4, ensure_ascii=False
    )
    print(website_info_json)


if __name__ == "__main__":
    main()
