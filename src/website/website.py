from bs4 import BeautifulSoup, Tag
from website import constants as Constants
from selenium import webdriver
from dataclasses import dataclass
from typing import Optional
import re
import urllib.parse as urlparse


@dataclass(frozen=True)
class WebsiteInfo:
    """The class contains the properties required for the parsing of the website.

    Attributes:
        found_urls (set[str]): A set of all the URLs found during the parsing process
        found_emails (dict[str, str]): A dictionary of all the emails found in the HTML content. Key: email, Value: Website URL

    Methods:
        to_dict(): A method that converts the WebsiteInfo object into a dictionary for JSON serialization
    """

    found_urls: set[str]
    found_emails: dict[str, str]

    def to_dict(self) -> dict:
        """Convert the WebsiteInfo object into a dictionary for JSON serialization."""
        return {
            "found_urls": list(self.found_urls),
            "found_emails": self.found_emails,
        }


# PUBLIC METHODS
def parse(website: str, info: Optional[WebsiteInfo] = None) -> WebsiteInfo:
    """Parse only the given website for information.

    Arguments:
        website (string): The website to parse

    Returns:
        WebsiteInfo: The information found during the parsing process
    """

    if info is None:
        new_info = WebsiteInfo(set(), dict())
    else:
        new_info: WebsiteInfo = info

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(website)
    website_page_source: str = driver.page_source
    content = BeautifulSoup(website_page_source, Constants.BEAUTIFULSOUP_HTML_PARSER)

    new_info.found_urls.update(get_links_from_html_content(website, content, new_info))
    new_info.found_emails.update(parse_for_emails(website, content, new_info))

    driver.quit()
    return new_info


def parse_all(website: str, number_of_sites_to_visit: int) -> WebsiteInfo:
    """Parse for links in the given website, then recursively parse the found sites for information.

    Arguments:
        website (str): The "root" website to parse
        number_of_sites_to_visit (int): The maximum number of sites to visit during parsing

    Returns:
        WebsiteInfo: The information found during the parsing process
    """

    visited_urls = set()
    info = WebsiteInfo(set(), dict())

    info: WebsiteInfo = parse(website, info)

    while len(visited_urls) != number_of_sites_to_visit - 1:
        for found_url in info.found_urls:
            if found_url not in visited_urls:
                new_info: WebsiteInfo = parse(found_url)
                visited_urls.add(found_url)
                info.found_urls.update(new_info.found_urls)
                info.found_emails.update(new_info.found_emails)
                break

    return info


def get_links_from_html_content(
    website_url: str, content: BeautifulSoup, info: WebsiteInfo
) -> set[str]:
    """Get all links from the given HTML content.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        info (WebsiteInfo): The information found during the parsing process

    Returns:
        A set of all the links found in the HTML content
    """

    found_urls: set[str] = info.found_urls
    hostname: str | None = urlparse.urlparse(website_url).hostname

    for link_tag in content.find_all(Constants.HTML_LINK_TAG):
        assert isinstance(link_tag, Tag)

        if not link_tag.has_attr(Constants.HTML_HREF):
            continue

        href = link_tag.attrs[Constants.HTML_HREF]
        assert isinstance(href, str)

        if href.startswith(Constants.SLASH) and not is_file_url(href):
            # Removing the last slash from the website URL if it exists to avoid double slashes
            if website_url.endswith((Constants.SLASH)):
                found_url: str = website_url[:-1] + href
            else:
                found_url = website_url + href
            found_urls.add(found_url)
        elif hostname is not None and hostname in href and not is_file_url(href):
            found_urls.add(href)

    return found_urls


def is_file_url(url: str) -> bool:
    """Check if the given URL is a file or a webpage.

    Arguments:
        url (str): The URL to check

    Returns:
        True if the URL is a file, False if it is a webpage
    """

    webpage_extensions: set[str] = Constants.WEBPAGE_EXTENSIONS
    path: str = urlparse.urlparse(url).path
    if Constants.EXTENSION_DOT in path:
        extension: str = path.split(Constants.EXTENSION_DOT)[1]
        if extension in webpage_extensions:
            return False
        else:
            return True

    return False


def parse_for_emails(
    website: str, content: BeautifulSoup, info: WebsiteInfo
) -> dict[str, str]:
    """Parse the given HTML content for emails.

    Arguments:
        website (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        info (WebsiteInfo): The information found during the parsing process

    Returns:
        A dictionary of all the emails found in the HTML content. Key: email, Value: Website URL
    """

    found_emails: dict[str, str] = info.found_emails
    html_content: str = content.decode()
    emails: list[str] = re.findall(Constants.EMAIL_REGEX, html_content)

    for email in emails:
        if email not in found_emails.keys():
            found_emails[email] = website

    return found_emails


# PRIVATE METHODS
