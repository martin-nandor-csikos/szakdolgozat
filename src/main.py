from website.website import WebsiteInfo
import sys
import website
import json


def main() -> None:
    website_to_parse: str = sys.argv[1]
    number_of_sites_to_visit = int(sys.argv[2])

    website_info: WebsiteInfo = website.parse_all(
        website_to_parse, number_of_sites_to_visit
    )
    website_info_json: str = json.dumps(website_info.to_dict(), indent=4)
    print(website_info_json)


if __name__ == "__main__":
    main()
