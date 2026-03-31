from dataclasses import dataclass

@dataclass(frozen=True)
class WebsiteInfo:
    """The class contains the properties required for the parsing of the website.

    Attributes:
        found_urls (set[str]): A set of all the URLs found during the parsing process
        found_emails (dict[str, str]): A dictionary of all the emails found in the HTML content. Key: email, Value: Website URL
        found_names (dict[str, str]): A dictionary of all the names found in the HTML content. Key: name, Value: Website URL
        found_phone_numbers (dict[str, str]): A dictionary of all the phone numbers found in the HTML content. Key: name, Value: Website URL
        found_addresses (dict[str, str]): A dictionary of all the addresses found in the HTML content. Key: name, Value: Website URL

    Methods:
        has_data() -> bool: Check if any data has been found during the parsing process. Links are not considered as data
    """

    found_urls: set[str]
    found_emails: dict[str, str]
    found_names: dict[str, str]
    found_phone_numbers: dict[str, str]
    found_addresses: dict[str, str]

    def has_data(self) -> bool:
        """Check if any data has been found during the parsing process.
        Only check for emails, names, phone numbers, and addresses.

        Returns:
            bool: True if any data has been found, False otherwise
        """
        return any([
            self.found_addresses,
            self.found_emails,
            self.found_names,
            self.found_phone_numbers,
        ])