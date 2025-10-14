from bs4 import BeautifulSoup, Tag, ResultSet
from functools import lru_cache
from rich.console import Console
from spacy.language import Language
from spacy.tokens.doc import Doc
from urllib import parse as urlparse
from website import constants as Constants
import phonenumbers
import re
import spacy
import validators

console = Console(log_path=False)
HU_MODEL = spacy.load(Constants.SPACY_MODEL_HU)
EN_MODEL = spacy.load(Constants.SPACY_MODEL_EN)

def get_sublinks(
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
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(found_urls, set):
        raise TypeError(f"Invalid found_urls type. Expected type: set, actual type: {type(found_urls)}")

    new_found_urls: set[str] = found_urls
    hostname: str | None = urlparse.urlparse(website_url).hostname

    # Loop through all the 'a' tags in the content and extract the links
    for link_tag in content.find_all(Constants.HTML_LINK_TAG):
        if not isinstance(link_tag, Tag):
            raise TypeError(f"Invalid link_tag type. Expected type: Tag, actual type: {type(link_tag)}")
        if not link_tag.has_attr(Constants.HTML_HREF):
            continue

        href: str = link_tag.attrs[Constants.HTML_HREF]
        website_url_stripped: str = website_url.rstrip(
            Constants.SPACE + Constants.SLASH
        )

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
            new_found_urls.add(found_url)

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
            new_found_urls.add(found_url)

    return new_found_urls

def get_emails(
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
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(found_emails, dict):
        raise TypeError(f"Invalid found_emails type. Expected type: dict, actual type: {type(found_emails)}")

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

def get_names(
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
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(found_names, dict):
        raise TypeError(f"Invalid found_names type. Expected type: dict, actual type: {type(found_names)}")

    new_found_names: dict[str, str] = found_names
    top_level_domain: str = urlparse.urlparse(website_url).netloc.split(".")[-1]
    nlp: Language = _get_spacy_model(top_level_domain)
    name_regex: re.Pattern[str] = re.compile(Constants.NAME_REGEX)
    text_tags: ResultSet[Tag] = content.find_all(
        Constants.HTML_TEXT_TAGS
    )

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

def get_phone_numbers(
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
    if not validators.url(website_url):
        raise ValueError(f"Invalid URL: {website_url}")
    if not isinstance(content, BeautifulSoup):
        raise TypeError(f"Invalid content type, Expected type: BeautifulSoup, actual type: {type(content)}")
    if not isinstance(found_phone_numbers, dict):
        raise TypeError(f"Invalid found_phone_numbers type. Expected type: dict, actual type: {type(found_phone_numbers)}")

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
        if not isinstance(phone_number_match, phonenumbers.PhoneNumberMatch):
            raise TypeError(f"Invalid phone_number_match type. Expected type: PhoneNumberMatch, actual type: {type(phone_number_match)}")

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
    
    return HU_MODEL if tld == Constants.HU_TOP_LEVEL_DOMAIN else EN_MODEL