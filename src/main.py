from website import WebsiteInfo, parse_all
import json
import sys
import validators

def main() -> None:
    """Main function of the program where the individual methods are called."""

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise ValueError("Wrong number of parameters. Usage: python main.py <website's URL to parse> <maximum number of subpages to visit (optional)>")
    if not validators.url(sys.argv[1]):
        raise ValueError(f"Invalid URL: {sys.argv[1]}. Example of a valid URL: https://www.example.com")
    if len(sys.argv) == 3:
        if not isinstance(int(sys.argv[2]), int):
            raise TypeError("Invalid sublinks_to_visit type. Must be an integer")
        if int(sys.argv[2]) < 1:
            raise ValueError("The maximum number of subpages to visit must be at least 1 or more")

    url: str = sys.argv[1]
    if len(sys.argv) == 3:
        sublinks_to_visit: int = int(sys.argv[2])
        website_info: WebsiteInfo = parse_all(url, sublinks_to_visit)
    else:
        website_info: WebsiteInfo = parse_all(url, 0)

    website_info_json: str = json.dumps(
        website_info.to_dict(), indent=4, ensure_ascii=False
    )
    print(website_info_json)

if __name__ == "__main__":
    main()
