from bs4 import BeautifulSoup, Tag, ResultSet
from bs4.element import NavigableString, PageElement
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from rich.console import Console
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from spacy.language import Language
from spacy.tokens.doc import Doc
from urllib import parse as urlparse
from website import constants as Constants
import phonenumbers
import re
import spacy
import tempfile
import validators

console = Console(log_path=False)

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
    found_phone_numbers: dict[str, str]

    def to_dict(self) -> dict:
        """Convert the WebsiteInfo object into a dictionary for JSON serialization."""
        return {
            "found_urls": list(self.found_urls),
            "found_emails": self.found_emails,
            "found_names": self.found_names,
            "found_phone_numbers": self.found_phone_numbers,
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
    options.add_argument('--headless')

    driver = webdriver.Remote("http://chrome_selenium:4444/wd/hub", options=options)
    driver.get(website_url)
    website_page_source: str = driver.page_source
    content = BeautifulSoup(website_page_source, Constants.BEAUTIFULSOUP_HTML_PARSER)
    driver.quit()

    # Parse the content for information with multiprocessing
    with ProcessPoolExecutor() as executor:
        links: Future[set[str]] = executor.submit(
            get_links_from_html_content, website_url, content, info.found_urls
        )
        emails: Future[dict[str, str]] = executor.submit(
            parse_for_emails, website_url, content, info.found_emails
        )
        names: Future[dict[str, str]] = executor.submit(
            parse_for_names, website_url, content, info.found_names
        )
        phone_numbers: Future[dict[str, str]] = executor.submit(
            parse_for_phone_numbers, website_url, content, info.found_phone_numbers
        )
        found_links: set[str] = links.result()
        found_emails: dict[str, str] = emails.result()
        found_names: dict[str, str] = names.result()
        found_phone_numbers: dict[str, str] = phone_numbers.result()

    return WebsiteInfo(found_links, found_emails, found_names, found_phone_numbers)


def parse_all(website_url: str, number_of_links_to_visit: int) -> WebsiteInfo:
    """Parse for links in the given website, then recursively parse the found links for information.

    Arguments:
        website_url (str): The website's URL to parse
        number_of_links_to_visit (int): The maximum number of links to visit and parse

    Returns:
        WebsiteInfo: The information found during the parsing process
    """
    assert validators.url(website_url), f"Invalid URL: {website_url}. Example of a valid URL: https://www.example.com"
    assert isinstance(number_of_links_to_visit, int), "Invalid number_of_links_to_visit"
    assert number_of_links_to_visit > 0, f"number_of_links_to_visit must be greater than 0 (actual: {number_of_links_to_visit})"

    visited_urls = set()
    info = WebsiteInfo(set(), dict(), dict(), dict())

    # Initial parsing of the website
    console.log(f"Parsing [link={website_url}]{website_url}[/link]")
    info: WebsiteInfo = parse(website_url, info)
    console.log(f"[green]Parsing completed[/green]")
    visited_urls.add(website_url)

    while True:
        if len(visited_urls) == number_of_links_to_visit or len(visited_urls) == len(
            info.found_urls
        ):
            break

        for found_url in info.found_urls:
            if found_url not in visited_urls:
                console.log(f"Parsing [link={found_url}]{found_url}[/link]")
                info: WebsiteInfo = parse(found_url, info)
                console.log(f"[green]Parsing completed[/green]")
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
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(content, BeautifulSoup), "Invalid BeautifulSoup object"
    assert isinstance(found_urls, set), "Invalid found_urls set"

    new_found_urls: set[str] = found_urls
    hostname: str | None = urlparse.urlparse(website_url).hostname

    # Loop through all the 'a' tags in the content and extract the links
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
        # Extract link that starts with a slash, like "/about"
        # File links are skipped
        if href.startswith(Constants.SLASH) and not is_file_url(href):
            if Constants.HTML_ID in href:
                href_stripped: str = href.split(Constants.HTML_ID)[0].rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                found_url: str = website_url_stripped + href_stripped
            else:
                found_url: str = website_url_stripped + href_stripped
            new_found_urls.add(found_url)

        # Extract full link
        # File links are skipped
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

    valid_webpage_extensions: set[str] = Constants.WEBPAGE_EXTENSIONS
    path: str = urlparse.urlparse(url).path
    if Constants.EXTENSION_DOT in path:
        extension: str = path.split(Constants.EXTENSION_DOT)[1]
        if extension not in valid_webpage_extensions:
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
            console.log(
                f"[yellow]FOUND EMAIL[/]: [cyan]{email}[/] on [link={website_url}]{website_url}[/link]"
            )

    return new_found_emails


@lru_cache(maxsize=2)
def load_spacy_model(tld: str) -> Language:
    """Load and cache the Spacy model based on the top-level domain.

    Arguments:
        tld (str): The top-level domain of the website

    Returns:
        The Spacy model to be loaded
    """
    if tld == Constants.HU_TOP_LEVEL_DOMAIN:
        return spacy.load(Constants.SPACY_MODEL_HU)
    return spacy.load(Constants.SPACY_MODEL_EN)


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
    nlp: Language = load_spacy_model(top_level_domain)
    name_regex: re.Pattern[str] = re.compile(Constants.NAME_REGEX)
    text_tags: ResultSet[Tag] = content.find_all(
        Constants.HTML_TEXT_TAGS
    )

    # Get all the relevant tags in the HTML content
    for tag in text_tags:
        assert isinstance(tag, Tag)

        tag_text: str = tag.text.strip()
        if not tag_text:
            continue

        doc: Doc = nlp(tag_text)

        # Loop through the entities to find names and add them to the dictionary
        for ent in doc.ents:
            name: str = ent.text
            if (
                (
                    ent.label_ == Constants.SPACY_ENTITY_PERSON_HUNGARIAN
                    or ent.label_ == Constants.SPACY_ENTITY_PERSON_ENGLISH
                )
                and name_regex.match(name)
                and name not in new_found_names.keys()
            ):
                new_found_names[name] = website_url.rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                console.log(
                    f"[yellow]FOUND NAME[/]: [cyan]{name}[/] on [link={website_url}]{website_url}[/link]"
                )

    return new_found_names


def parse_for_phone_numbers(
    website_url: str, content: BeautifulSoup, found_phone_numbers: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for phone numbers.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_phone_numbers (dict): Previously found phone numbers

    Returns:
        A dictionary of all the phone numbers found in the HTML content. Key: phone number, Value: URL where the number was found
    """
    assert validators.url(website_url), f"Invalid URL: {website_url}"
    assert isinstance(content, BeautifulSoup), "Invalid BeautifulSoup object"
    assert isinstance(
        found_phone_numbers, dict
    ), "Invalid found_phone_numbers dictionary"

    new_found_phone_numbers: dict[str, str] = found_phone_numbers
    html_content: str = content.decode()
    top_level_domain: str = urlparse.urlparse(website_url).netloc.split(".")[-1]

    # The UK TLD is replaced with GB for phone number parsing, every other ccTLD matches the ISO code
    if top_level_domain == Constants.UK_TOP_LEVEL_DOMAIN:
        top_level_domain = Constants.GB_ISO_CODE

    # If the TLD is 2 characters long, it's a country code except for EU and SU
    # If not, it's an unknown region ("ZZ")
    if (
        len(top_level_domain) == 2
        and top_level_domain
        not in Constants.NON_COUNTRY_TOP_LEVEL_DOMAIN_WITH_TWO_LETTERS
    ):
        phone_number_region: str = top_level_domain.upper()
    else:
        phone_number_region: str = Constants.PHONE_NUMBER_UNKNOWN_REGION

    # Iterate through the phone number matches
    for phone_number_match in phonenumbers.PhoneNumberMatcher(
        html_content, phone_number_region
    ):
        assert isinstance(phone_number_match, phonenumbers.PhoneNumberMatch)

        # Format the phone number for consistency
        phone_number: str = phonenumbers.format_number(
            phone_number_match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        if phone_number not in new_found_phone_numbers.keys():
            new_found_phone_numbers[phone_number] = website_url.rstrip(
                Constants.SPACE + Constants.SLASH
            )
            console.log(
                f"[yellow]FOUND PHONE NUMBER[/]: [cyan]{phone_number}[/] on [link={website_url}]{website_url}[/link]"
            )

    return new_found_phone_numbers
