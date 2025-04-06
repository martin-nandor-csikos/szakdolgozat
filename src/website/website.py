from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from selenium import webdriver
from typing import Optional
from urllib import parse as urlparse
from website import constants as Constants
import re


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
def parse(website_url: str, info: WebsiteInfo) -> WebsiteInfo:
    """Parse the given website for information.

    Arguments:
        website_url (str): The website's URL to parse
        info (WebsiteInfo): Object of the already found information

    Returns:
        WebsiteInfo: The information found during the parsing process
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(website_url)
    website_page_source: str = driver.page_source
    content = BeautifulSoup(website_page_source, Constants.BEAUTIFULSOUP_HTML_PARSER)
    driver.quit()

    return WebsiteInfo(
        get_links_from_html_content(website_url, content, info.found_urls),
        parse_for_emails(website_url, content, info.found_emails),
    )


def parse_all(website_url: str, number_of_links_to_visit: int) -> WebsiteInfo:
    """Parse for links in the given website, then recursively parse the found links for information.

    Arguments:
        website_url (str): The website's URL to parse
        number_of_links_to_visit (int): The maximum number of links to visit and parse

    Returns:
        WebsiteInfo: The information found during the parsing process
    """

    visited_urls = set()
    info = WebsiteInfo(set(), dict())

    # Initial parsing of the website
    info: WebsiteInfo = parse(website_url, info)
    visited_urls.add(website_url)

    while len(visited_urls) != number_of_links_to_visit:
        for found_url in info.found_urls:
            if found_url not in visited_urls:
                info: WebsiteInfo = parse(found_url, info)
                visited_urls.add(found_url)
                break

    return info


def get_links_from_html_content(
    website_url: str, content: BeautifulSoup, found_urls: set[str]
) -> set[str]:
    """Get all links from the given HTML content.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        info (WebsiteInfo): Object of the already found information

    Returns:
        A set of all the links found in the HTML content
    """

    new_found_urls: set[str] = found_urls
    hostname: str | None = urlparse.urlparse(website_url).hostname

    for link_tag in content.find_all(Constants.HTML_LINK_TAG):
        assert isinstance(link_tag, Tag)

        if not link_tag.has_attr(Constants.HTML_HREF):
            continue

        href = link_tag.attrs[Constants.HTML_HREF]
        assert isinstance(href, str)

        website_url_stripped: str = website_url.rstrip(
            Constants.SPACE + Constants.SLASH
        )

        href_stripped: str = href.rstrip(Constants.SPACE + Constants.SLASH)
        if href.startswith(Constants.SLASH) and not is_file_url(href):
            if Constants.HTML_ID in href:
                href_stripped: str = href.split(Constants.HTML_ID)[0].rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                found_url: str = website_url_stripped + href_stripped
            else:
                found_url: str = website_url_stripped + href_stripped
            new_found_urls.add(found_url)

        if hostname is not None and hostname in href and not is_file_url(href):
            if Constants.HTML_ID in href:
                href_stripped: str = href.split(Constants.HTML_ID)[0].rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                found_url: str = href_stripped.split(Constants.HTML_ID)[0]
            else:
                found_url: str = href_stripped
            new_found_urls.add(found_url)

    return new_found_urls


def is_file_url(url: str) -> bool:
    """Check if the given URL is a file or not.

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
        return True

    return False


def parse_for_emails(
    website_url: str, content: BeautifulSoup, found_emails: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for emails.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        info (WebsiteInfo): Object of the already found information

    Returns:
        A dictionary of all the emails found in the HTML content. Key: email, Value: URL where the email was found
    """

    new_found_emails: dict[str, str] = found_emails
    html_content: str = content.decode()
    emails: list[str] = re.findall(Constants.EMAIL_REGEX, html_content)

    for email in emails:
        if email not in new_found_emails.keys():
            new_found_emails[email] = website_url.rstrip(
                Constants.SPACE + Constants.SLASH
            )

    return new_found_emails
