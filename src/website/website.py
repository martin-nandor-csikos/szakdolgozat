from bs4 import BeautifulSoup
from concurrent.futures import Future, ProcessPoolExecutor
from collections import deque
from rich.console import Console
from selenium import webdriver
from website import constants as Constants
from .models import WebsiteInfo
from .data_extractors import *
import spacy
import validators

console = Console(log_path=False)
HU_MODEL = spacy.load(Constants.SPACY_MODEL_HU)
EN_MODEL = spacy.load(Constants.SPACY_MODEL_EN)

def parse(website_url: str, info: WebsiteInfo) -> WebsiteInfo:
    """Parse the given website for information.

    Arguments:
        website_url (str): The website's URL to parse
        info (WebsiteInfo): Object of the already found information

    Returns:
        WebsiteInfo: The information found during the parsing process
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(info, WebsiteInfo):
        raise TypeError(f"Invalid info type. Expected type: WebsiteInfo, actual type: {type(info)}")

    content: BeautifulSoup = _get_website_content(website_url)

    # Parse the content for information with multiprocessing
    with ProcessPoolExecutor() as executor:
        links: Future[set[str]] = executor.submit(
            get_sublinks, website_url, content, info.found_urls
        )
        emails: Future[dict[str, str]] = executor.submit(
            get_emails, website_url, content, info.found_emails
        )
        names: Future[dict[str, str]] = executor.submit(
            get_names, website_url, content, info.found_names
        )
        phone_numbers: Future[dict[str, str]] = executor.submit(
            get_phone_numbers, website_url, content, info.found_phone_numbers
        )

        found_links: set[str] = links.result()
        found_emails: dict[str, str] = emails.result()
        found_names: dict[str, str] = names.result()
        found_phone_numbers: dict[str, str] = phone_numbers.result()

    return WebsiteInfo(found_links, found_emails, found_names, found_phone_numbers)

def parse_all(website_url: str, sublinks_to_visit: int) -> WebsiteInfo:
    """Parse for links in the given website, then recursively parse the found links for information.

    Arguments:
        website_url (str): The website's URL to parse
        number_of_links_to_visit (int): The maximum number of links to visit and parse

    Returns:
        WebsiteInfo: The information found during the parsing process
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(sublinks_to_visit, int):
        raise TypeError(f"Invalid sublinks_to_visit type. Expected type: int, actual type: {type(sublinks_to_visit)}")
    if sublinks_to_visit < 0:
            raise ValueError("The maximum number of subpages to visit must be at least 0 or more")

    visited_urls: set = set()
    url_queue: deque[str] = deque([website_url])
    info: WebsiteInfo = WebsiteInfo(set(), dict(), dict(), dict())
    websites_parsed: int = 0

    # If sublinks to visit 0, only visit the main page
    # If it's more than 0, visit the main page + the given number of sublinks
    if sublinks_to_visit == 0:
        max_visits = 1
    else:
        max_visits = sublinks_to_visit + 1

    while url_queue and websites_parsed < max_visits:
        # Get the next URL from the queue
        url = url_queue.popleft()
        if url in visited_urls:
            continue

        with console.status(f"Parsing [link={url}]{url}[/link]", spinner="dots"):
            info = parse(url, info)
        console.log(f"[green]Parsing completed[/green]")
        visited_urls.add(url)
        websites_parsed += 1

        # Add the found URLs to the queue if they haven't been visited yet
        for found_url in info.found_urls:
            if found_url not in visited_urls and found_url not in url_queue:
                url_queue.append(found_url)


    if websites_parsed < sublinks_to_visit:
        console.log(f"[yellow]Only {websites_parsed} subpages could be parsed.[/yellow]")
    return info

def _get_website_content(url: str) -> BeautifulSoup:
    """Get the HTML content of the given website.

    Arguments:
        url (str): The website's URL

    Returns:
        BeautifulSoup: The HTML content of the website
    """
    if not validators.url(url):
        raise ValueError(f"Invalid URL: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Remote("http://chrome_selenium:4444/wd/hub", options=options)
    driver.get(url)
    website_page_source: str = driver.page_source
    content = BeautifulSoup(website_page_source, Constants.BEAUTIFULSOUP_HTML_PARSER)
    driver.quit()

    return content