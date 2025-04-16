from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from selenium import webdriver
from spacy.language import Language
from urllib import parse as urlparse

from spacy.tokens.doc import Doc
from website import constants as Constants
import re
import spacy
import validators


@dataclass(frozen=True)
class WebsiteInfo:
    """The class contains the properties required for the parsing of the website.

    Attributes:
        found_urls (set[str]): A set of all the URLs found during the parsing process
        found_emails (dict[str, str]): A dictionary of all the emails found in the HTML content. Key: email, Value: Website URL
        found_names (dict[str, str]): A dictionary of all the names found in the HTML content. Key: name, Value: Website URL

    Methods:
        to_dict(): A method that converts the WebsiteInfo object into a dictionary for JSON serialization
    """

    found_urls: set[str]
    found_emails: dict[str, str]
    found_names: dict[str, str]

    def to_dict(self) -> dict:
        """Convert the WebsiteInfo object into a dictionary for JSON serialization."""
        return {
            "found_urls": list(self.found_urls),
            "found_emails": self.found_emails,
            "found_names": self.found_names,
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
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(info, WebsiteInfo), "Invalid WebsiteInfo object"

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
        parse_for_names(website_url, content, info.found_names),
    )


def parse_all(website_url: str, number_of_links_to_visit: int) -> WebsiteInfo:
    """Parse for links in the given website, then recursively parse the found links for information.

    Arguments:
        website_url (str): The website's URL to parse
        number_of_links_to_visit (int): The maximum number of links to visit and parse

    Returns:
        WebsiteInfo: The information found during the parsing process
    """
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(number_of_links_to_visit, int), "Invalid number_of_links_to_visit"
    assert (
        number_of_links_to_visit > 0
    ), "number_of_links_to_visit must be greater than 0"

    visited_urls = set()
    info = WebsiteInfo(set(), dict(), dict())

    # Initial parsing of the website
    info: WebsiteInfo = parse(website_url, info)
    visited_urls.add(website_url)

    while True:
        if len(visited_urls) == number_of_links_to_visit:
            break

        for found_url in info.found_urls:
            if found_url not in visited_urls:
                info: WebsiteInfo = parse(found_url, info)
                visited_urls.add(found_url)
                break

        # If there are no more new URLs to visit, break the loop
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
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(content, BeautifulSoup), "Invalid BeautifulSoup object"
    assert isinstance(found_urls, set), "Invalid found_urls set"

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
    assert isinstance(url, str), "Invalid URL: must be a string"

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
        found_emails (dict): Previously found emails

    Returns:
        A dictionary of all the emails found in the HTML content. Key: email, Value: URL where the email was found
    """
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(content, BeautifulSoup), "Invalid BeautifulSoup object"
    assert isinstance(found_emails, dict), "Invalid found_emails dictionary"

    new_found_emails: dict[str, str] = found_emails
    html_content: str = content.decode()
    emails: list[str] = re.findall(Constants.EMAIL_REGEX, html_content)

    for email in emails:
        if email not in new_found_emails.keys():
            new_found_emails[email] = website_url.rstrip(
                Constants.SPACE + Constants.SLASH
            )

    return new_found_emails


def parse_for_names(
    website_url: str, content: BeautifulSoup, found_names: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for names.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_names (dict): Previously found names

    Returns:
        A dictionary of all the names found in the HTML content. Key: name, Value: URL where the name was found
    """
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(content, BeautifulSoup), "Invalid BeautifulSoup object"
    assert isinstance(found_names, dict), "Invalid found_names dictionary"

    new_found_names: dict[str, str] = found_names
    top_level_domain: str = urlparse.urlparse(website_url).netloc.split(".")[-1]

    # Load the spacy model based on the top-level domain (for better accuracy and detection)
    if top_level_domain == Constants.HU_TOP_LEVEL_DOMAIN:
        nlp: Language = spacy.load("hu_core_news_lg")
    else:
        nlp: Language = spacy.load("en_core_web_lg")

    # Get all the tags in the HTML content
    for tag in content.find_all():
        assert isinstance(tag, Tag)

        # If tag is not in the text tags, skip it (likely it doesn't contain text)
        if tag.name not in Constants.HTML_TEXT_TAGS:
            continue

        doc: Doc = nlp(tag.text.strip())

        # Loop through the entities to find names
        for ent in doc.ents:
            if (
                ent.label_ == Constants.SPACY_ENTITY_PERSON_HUNGARIAN
                or ent.label_ == Constants.SPACY_ENTITY_PERSON_ENGLISH
            ):
                # In case there are multiple names in the entity, loop through them and add each
                found_name: list[str] = re.findall(
                    Constants.NAME_REGEX, ent.text.strip()
                )
                for name in found_name:
                    if name not in new_found_names.keys():
                        new_found_names[name] = website_url.rstrip(
                            Constants.SPACE + Constants.SLASH
                        )

    return new_found_names
