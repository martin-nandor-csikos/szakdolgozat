from bs4 import BeautifulSoup, Tag, ResultSet
from concurrent.futures import Future, ProcessPoolExecutor
from functools import lru_cache
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
import validators

console = Console(log_path=False)

def get_data_from_content(
    info: WebsiteInfo, website_url: str, content: BeautifulSoup
) -> WebsiteInfo:
    """Parse the given HTML content for information.

    Arguments:
        info (WebsiteInfo): Object of the already found information
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse

    Returns:
        WebsiteInfo: The information found during the parsing process
    """
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
        addresses: Future[dict[str, str]] = executor.submit(
            get_addresses, website_url, content, info.found_phone_numbers
        )

        found_links: set[str] = links.result()
        found_emails: dict[str, str] = emails.result()
        found_names: dict[str, str] = names.result()
        found_phone_numbers: dict[str, str] = phone_numbers.result()
        found_addresses: dict[str, str] = addresses.result()

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
    website_url_stripped: str = website_url.rstrip(Constants.SPACE + Constants.SLASH)

    # Loop through all the 'a' tags in the content and extract the links
    for link_tag in content.find_all(Constants.HTML_LINK_TAG):
        if not isinstance(link_tag, Tag):
            raise TypeError(f"Invalid link_tag type. Expected type: Tag, actual type: {type(link_tag)}")
        if not link_tag.has_attr(Constants.HTML_HREF):
            continue

        href: str = str(link_tag.attrs[Constants.HTML_HREF])
        href_stripped: str = href.rstrip(Constants.SPACE + Constants.SLASH)
        # Extract link that starts with a slash, like "/about"
        # File links are skipped
        if href.startswith(Constants.SLASH) and not _is_file_url(href):
            if Constants.HTML_ID in href:
                href_stripped: str = href.split(Constants.HTML_ID)[0].rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                found_url: str = website_url_stripped + href_stripped
            else:
                found_url: str = website_url_stripped + href_stripped
            new_urls.add(found_url)

        # Extract full link
        # File links are skipped
        if hostname is not None and hostname in href and not _is_file_url(href):
            if Constants.HTML_ID in href:
                href_stripped: str = href.split(Constants.HTML_ID)[0].rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                found_url: str = href_stripped.split(Constants.HTML_ID)[0]
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
    html_content: str = content.decode()
    emails: list[str] = re.findall(Constants.EMAIL_REGEX, html_content)

    for email in emails:
        if email not in new_emails.keys():
            new_emails[email] = website_url.rstrip(
                Constants.SPACE + Constants.SLASH
            )
            console.log(
                f"[yellow]FOUND EMAIL[/]: [cyan]{email}[/] on [link={website_url}]{website_url}[/link]"
            )

    return new_emails

def get_names(
    website_url: str, content: BeautifulSoup, previous_names: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for names.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_names (dict): Previously found names

    Returns:
        A dictionary of all the names found in the HTML content. Key: name, Value: URL where the name was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_names, dict):
        raise TypeError(f"Invalid previous_names type. Expected type: dict, actual type: {type(previous_names)}")

    new_names: dict[str, str] = previous_names
    top_level_domain: str = urlparse.urlparse(website_url).netloc.split(".")[-1]
    nlp: Language = _get_spacy_model(top_level_domain)
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
                new_names[name] = website_url.rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                console.log(
                    f"[yellow]FOUND NAME[/]: [cyan]{name}[/] on [link={website_url}]{website_url}[/link]"
                )

    return new_names

def get_phone_numbers(
    website_url: str, content: BeautifulSoup, previous_phone_numbers: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for phone numbers.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_phone_numbers (dict): Previously found phone numbers

    Returns:
        A dictionary of all the phone numbers found in the HTML content. Key: phone number, Value: URL where the number was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_phone_numbers, dict):
        raise TypeError(f"Invalid previous_phone_numbers type. Expected type: dict, actual type: {type(previous_phone_numbers)}")

    new_phone_numbers: dict[str, str] = previous_phone_numbers
    html_content: str = content.decode()
    top_level_domain = _get_tld(website_url)

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

    website_url_stripped: str = website_url.rstrip(Constants.SPACE + Constants.SLASH)

    # Iterate through the phone number matches
    for phone_number_match in phonenumbers.PhoneNumberMatcher(
        html_content, phone_number_region
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

    return new_phone_numbers

def get_addresses(
    website_url: str, content: BeautifulSoup, previous_addresses: dict[str, str]
) -> dict[str, str]:
    """Parse the given HTML content for addresses.

    Arguments:
        website_url (str): The website's URL
        content (BeautifulSoup): The HTML content to parse
        found_addresses (dict): Previously found addresses

    Returns:
        A dictionary of all the names found in the HTML content. Key: name, Value: URL where the name was found
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(previous_addresses, dict):
        raise TypeError(f"Invalid previous_addresses type. Expected type: dict, actual type: {type(previous_addresses)}")

    new_addresses: dict[str, str] = previous_addresses
    text_tags: ResultSet[Tag] = content.find_all(Constants.HTML_TEXT_TAGS)

    # Get all the relevant tags in the HTML content
    for tag in text_tags:
        if not isinstance(tag, Tag):
            raise TypeError(f"Invalid tag type. Expected type: Tag, actual type: {type(tag)}")

        tag_text: str = tag.text.strip()
        if not tag_text:
            continue

        parsed_address = parse_address(tag_text, _get_tld(website_url))

        # 3 is an arbitrary threshold to filter out non-addresses
        min_component_count = 3
        if len(parsed_address) > min_component_count:
            # Reconstruct the address from the parsed components
            full_address = " ".join(component for component, label in parsed_address)

            if full_address not in new_addresses.keys():
                new_addresses[full_address] = website_url.rstrip(
                    Constants.SPACE + Constants.SLASH
                )
                console.log(
                    f"[yellow]FOUND ADDRESS[/]: [cyan]{full_address}[/] on [link={website_url}]{website_url}[/link]"
                )

    return new_addresses

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
    if Constants.EXTENSION_DOT in path:
        extension: str = path.split(Constants.EXTENSION_DOT)[1]
        if extension not in valid_webpage_extensions:
            return True

    return False

@lru_cache(maxsize=1)
def _get_hu_model()-> Language:
    """Get the hungarian Spacy model.

    Returns:
        Hungarian Spacy model
    """
    return spacy.load(Constants.SPACY_MODEL_HU)

@lru_cache(maxsize=1)
def _get_en_model() -> Language:
    """Get the english Spacy model.

    Returns:
        English Spacy model
    """
    return spacy.load(Constants.SPACY_MODEL_EN)

@lru_cache(maxsize=2)
def _get_spacy_model(tld: str) -> Language:
    """Return the Spacy model based on the top-level domain.

    Arguments:
        tld (str): The top-level domain of the website

    Returns:
        The Spacy model to be returned
    """
    if not isinstance(tld, str):
        raise TypeError(f"Invalid tld type. Expected type: str, actual type: {type(tld)}")
    
    if tld == Constants.HU_TOP_LEVEL_DOMAIN:
        return _get_hu_model()
    return _get_en_model()

def _get_tld(website_url: str) -> str:
    """Get the top-level domain from the given website URL.

    Arguments:
        website_url (str): The website's URL
    Returns:
        The top-level domain of the website
    """
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    
    return urlparse.urlparse(website_url).netloc.split(".")[-1]