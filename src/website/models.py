from dataclasses import dataclass

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