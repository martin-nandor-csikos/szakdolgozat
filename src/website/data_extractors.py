from bs4 import BeautifulSoup, Tag, ResultSet
from functools import lru_cache
from globals.enums import DataRegion
from postal.parser import parse_address
from rich.console import Console
from spacy.language import Language
from spacy.tokens.doc import Doc
from urllib import parse as urlparse
from website import constants as Constants
from .models import WebsiteInfo
import phonenumbers
import re
import spacy
import threading
import validators

console = Console(log_path=False)
information_printed = threading.Event()

def get_data_from_content(
    info: WebsiteInfo, website_url: str, content: BeautifulSoup, region: DataRegion
) -> WebsiteInfo:
    """Parse the given HTML content for information.

    Arguments:
        info (WebsiteInfo): Object of the already found information
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        region (DataRegion): The primary region for data to be found

    Returns:
        WebsiteInfo: The information found during the parsing process
    """
    found_links = get_sublinks(website_url, content, info.found_urls)
    found_emails = get_emails(website_url, content, info.found_emails)
    found_names = get_names(website_url, content, info.found_names, region)
    found_phone_numbers = get_phone_numbers(website_url, content, info.found_phone_numbers, region)
    found_addresses = get_addresses(website_url, content, info.found_addresses, region)

    return WebsiteInfo(found_links, found_emails, found_names, found_phone_numbers, found_addresses)

def get_sublinks(
    website_url: str, content: BeautifulSoup, previous_urls: set[str]
) -> set[str]:
    """Get all links from the given HTML content.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        info (WebsiteInfo): Object of the already found information

    Returns:
        A set of all the links found in the HTML content
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_urls, set):
        raise TypeError(f"Invalid previous_urls type. Expected type: set, actual type: {type(previous_urls)}")

    new_urls: set[str] = previous_urls
    hostname: str | None = urlparse.urlparse(website_url).hostname
    website_url_stripped: str = _get_stripped_link(website_url)

    # Loop through all the 'a' tags in the content and extract the links
    for link_tag in content.find_all("a"):
        if not isinstance(link_tag, Tag):
            raise TypeError(f"Invalid link_tag type. Expected type: Tag, actual type: {type(link_tag)}")
        if not link_tag.has_attr("href"):
            continue

        href: str = str(link_tag.attrs["href"])
        href_stripped: str = _get_stripped_link(href)
        # Extract link that starts with a slash, like "/about"
        # File links are skipped
        if href.startswith("/") and not _is_file_url(href):
            if "#" in href:
                href_stripped: str = href.split("#")[0].rstrip(
                    " /"
                )
                found_url: str = website_url_stripped + href_stripped
            else:
                found_url: str = website_url_stripped + href_stripped
            new_urls.add(found_url)

        # Extract full link
        # File links are skipped
        if hostname is not None and hostname in href and not _is_file_url(href):
            if "#" in href:
                href_stripped: str = href.split("#")[0].rstrip(
                    " /"
                )
                found_url: str = href_stripped.split("#")[0]
            else:
                found_url: str = href_stripped
            new_urls.add(found_url)

    return new_urls

def get_emails(
    website_url: str, content: BeautifulSoup, previous_emails: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for emails.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_emails (dict): Previously found emails

    Returns:
        A dictionary of all the emails found in the HTML content. Key: email, Value: URL where the email was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_emails, dict):
        raise TypeError(f"Invalid previous_emails type. Expected type: dict, actual type: {type(previous_emails)}")

    new_emails: dict[str, str] = previous_emails
    text_tags: ResultSet[Tag] = content.find_all(Constants.HTML_TEXT_TAGS)

    for tag in text_tags:
        if not isinstance(tag, Tag):
            raise TypeError(f"Invalid tag type. Expected type: Tag, actual type: {type(tag)}")

        tag_text: str = tag.text.strip()
        if not tag_text:
            continue

        emails: list[str] = re.findall(Constants.EMAIL_REGEX, tag_text)

        for email in emails:
            if email not in new_emails.keys():
                new_emails[email] = website_url.rstrip(" /")
                console.log(
                    f"[yellow]FOUND EMAIL[/]: [cyan]{email}[/] on [link={website_url}]{website_url}[/link]"
                )
                set_information_printed()

    return new_emails

def get_names(
    website_url: str, content: BeautifulSoup, previous_names: dict[str, str], region: DataRegion
) -> dict[str, str]:
    """Parse the given HTML content for names.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_names (dict): Previously found names
        region (DataRegion): The primary region for data to be found

    Returns:
        A dictionary of all the names found in the HTML content. Key: name, Value: URL where the name was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_names, dict):
        raise TypeError(f"Invalid previous_names type. Expected type: dict, actual type: {type(previous_names)}")
    if not isinstance(region, DataRegion):
        raise TypeError(f"Invalid region type. Expected type: DataRegion, actual type: {type(region)}")

    new_names: dict[str, str] = previous_names
    nlp: Language = _get_spacy_model(region)
    name_regex: re.Pattern[str] = re.compile(Constants.NAME_REGEX)
    text_tags: ResultSet[Tag] = content.find_all(Constants.HTML_TEXT_TAGS)

    # Get all the relevant tags in the HTML content
    for tag in text_tags:
        if not isinstance(tag, Tag):
            raise TypeError(f"Invalid tag type. Expected type: Tag, actual type: {type(tag)}")

        tag_text: str = tag.text.strip()
        if not tag_text:
            continue

        doc: Doc = nlp(tag_text)

        # Loop through the entities to find names and add them to the dictionary
        for ent in doc.ents:
            name: str = ent.text
            if (
                ent.label_ in (Constants.SPACY_ENTITY_PERSON_HUNGARIAN, Constants.SPACY_ENTITY_PERSON_ENGLISH)
                and name_regex.match(name)
                and name not in new_names.keys()
            ):
                new_names[name] = website_url.rstrip(" /")
                console.log(
                    f"[yellow]FOUND NAME[/]: [cyan]{name}[/] on [link={website_url}]{website_url}[/link]"
                )
                set_information_printed()

    return new_names

def get_phone_numbers(
    website_url: str, content: BeautifulSoup, previous_phone_numbers: dict[str, str], region: DataRegion
) -> dict[str, str]:
    """Parse the given HTML content for phone numbers.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_phone_numbers (dict): Previously found phone numbers
        region (DataRegion): The primary region for data to be found

    Returns:
        A dictionary of all the phone numbers found in the HTML content. Key: phone number, Value: URL where the number was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_phone_numbers, dict):
        raise TypeError(f"Invalid previous_phone_numbers type. Expected type: dict, actual type: {type(previous_phone_numbers)}")
    if not isinstance(region, DataRegion):
        raise TypeError(f"Invalid region type. Expected type: DataRegion, actual type: {type(region)}")

    new_phone_numbers: dict[str, str] = previous_phone_numbers
    html_content: str = content.decode()

    website_url_stripped: str = _get_stripped_link(website_url)

    # Iterate through the phone number matches
    for phone_number_match in phonenumbers.PhoneNumberMatcher(
        html_content, region.value.upper()
    ):
        if not isinstance(phone_number_match, phonenumbers.PhoneNumberMatch):
            raise TypeError(f"Invalid phone_number_match type. Expected type: PhoneNumberMatch, actual type: {type(phone_number_match)}")

        # Format the phone number for consistency
        phone_number: str = phonenumbers.format_number(
            phone_number_match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        if phone_number not in new_phone_numbers.keys():
            new_phone_numbers[phone_number] = website_url_stripped
            console.log(
                f"[yellow]FOUND PHONE NUMBER[/]: [cyan]{phone_number}[/] on [link={website_url}]{website_url}[/link]"
            )
            set_information_printed()

    return new_phone_numbers

def get_addresses(
    website_url: str, content: BeautifulSoup, previous_addresses: dict[str, str], region: DataRegion
) -> dict[str, str]:
    """Parse the given HTML content for addresses.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_addresses (dict): Previously found addresses
        region (DataRegion): The primary region for data to be found

    Returns:
        A dictionary of all the addresses found in the HTML content. Key: address, Value: URL where the address was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_addresses, dict):
        raise TypeError(f"Invalid previous_addresses type. Expected type: dict, actual type: {type(previous_addresses)}")
    if not isinstance(region, DataRegion):
        raise TypeError(f"Invalid region type. Expected type: DataRegion, actual type: {type(region)}")

    new_addresses: dict[str, str] = previous_addresses
    text_tags: ResultSet[Tag] = content.find_all(Constants.HTML_TEXT_TAGS)

    # Get all the relevant tags in the HTML content
    for tag in text_tags:
        if not isinstance(tag, Tag):
            raise TypeError(f"Invalid tag type. Expected type: Tag, actual type: {type(tag)}")

        tag_text: str = tag.text.strip()
        if not tag_text:
            continue

        parsed_address = parse_address(tag_text, country=region.value.upper())
        
        # Skip empty results
        if not parsed_address:
            continue

        parsed_dict = dict(parsed_address)
        # Check for essential components to avoid false positives
        if all(component in parsed_dict.values() for component in Constants.ESSENTIAL_ADDRESS_COMPONENTS):
            # Min and Max are an arbitrary threshold to filter out non-addresses
            if len(parsed_address) > Constants.MIN_ADDRESS_COMPONENTS and len(parsed_address) < Constants.MAX_ADDRESS_COMPONENTS:
                # Reconstruct the address from the parsed components
                full_address = " ".join(component for component, label in parsed_address)

                if full_address not in new_addresses.keys():
                    new_addresses[full_address] = _get_stripped_link(website_url)
                    console.log(
                        f"[yellow]FOUND ADDRESS[/]: [cyan]{full_address}[/] on [link={website_url}]{website_url}[/link]"
                    )
                    set_information_printed()

    return new_addresses

def set_information_printed():
    """Set the data found flag to indicate that some data has been found during the parsing process."""
    global information_printed
    information_printed.set()

def _is_file_url(url: str) -> bool:
    """Check if the given URL is a file or not.

    Arguments:
        url (str): The URL to check

    Returns:
        True if the URL is a file, False if it is a webpage
    """
    if not isinstance(url, str):
        raise TypeError(f"Invalid URL type. Expected type: str, actual type: {type(url)}")
    
    valid_webpage_extensions: set[str] = Constants.WEBPAGE_EXTENSIONS
    path: str = urlparse.urlparse(url).path
    if "." in path:
        extension: str = path.split(".")[1]
        if extension not in valid_webpage_extensions:
            return True

    return False

@lru_cache(maxsize=Constants.LRU_CACHE_MAXSIZE)
def _get_spacy_model(region: DataRegion) -> Language:
    """Return the Spacy model based on the region.

    Arguments:
        region (DataRegion): The region of the website

    Returns:
        The Spacy model to be returned
    """
    if not isinstance(region, DataRegion):
        raise TypeError(f"Invalid region type. Expected type: DataRegion, actual type: {type(region)}")
    
    if region == DataRegion.HUNGARY:
        return spacy.load(Constants.SPACY_MODEL_HU)
    return spacy.load(Constants.SPACY_MODEL_EN)

def _get_stripped_link(link: str) -> str:
    """Get the stripped version of the given link.

    Arguments:
        link (str): A link to a website
    Returns:
        str: Stripped version of the link
    """
    return link.rstrip(" /")