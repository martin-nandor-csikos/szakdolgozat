import requests
from bs4 import BeautifulSoup
import sys

found_urls = []
visited_urls = []
number_of_pages_visited = 1

def find_links(webpage, number_of_pages_to_visit):
    global number_of_pages_visited

    main_site_request = requests.get(webpage)
    main_site_request_html = BeautifulSoup(main_site_request.text, "html.parser")

    for i in main_site_request_html.find_all("a"):
        href = i.attrs["href"]

        if href.startswith("/"):
            found_url = webpage + href

            if (found_url not in found_urls and ".pdf" not in found_url):
                found_urls.append(found_url)

    print(f"found url size: {len(found_urls)}")
    print(visited_urls)

    parse_site_for_information(webpage)

    visited_urls.append(webpage)
    for found_url in found_urls:
        if (found_url not in visited_urls and number_of_pages_to_visit != number_of_pages_visited):
            number_of_pages_visited += 1
            find_links(found_url, number_of_pages_to_visit)

def parse_site_for_information(webpage):
    pass

find_links(sys.argv[1], int(sys.argv[2]))
