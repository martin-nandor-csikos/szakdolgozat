from website.models import WebsiteInfo

def get_mock_website_info_with_all_data() -> WebsiteInfo:
    """Return a WebsiteInfo object with all data types populated."""
    return WebsiteInfo(
        found_urls={"https://example.com", "https://example.com/page1", "https://example.com/page2"},
        found_emails={
            "john@example.com": "https://example.com",
            "jane@example.com": "https://example.com/page1",
            "contact@company.org": "https://example.com/page2",
        },
        found_names={
            "John Doe": "https://example.com",
            "Jane Smith": "https://example.com/page1",
        },
        found_phone_numbers={
            "+36 30 123 4567": "https://example.com",
            "+1 555 0123": "https://example.com/page1",
        },
        found_addresses={
            "123 Main St, Springfield, IL 62704": "https://example.com",
            "456 Elm St, Budapest, 1051": "https://example.com/page1",
        },
    )

def get_mock_website_info_with_names_only() -> WebsiteInfo:
    """Return a WebsiteInfo object with only names."""
    return WebsiteInfo(
        found_urls={"https://example.com"},
        found_emails={},
        found_names={
            "John Doe": "https://example.com",
            "Jane Smith": "https://example.com",
        },
        found_phone_numbers={},
        found_addresses={},
    )

def get_mock_website_info_empty() -> WebsiteInfo:
    """Return an empty WebsiteInfo object."""
    return WebsiteInfo(
        found_urls=set(),
        found_emails={},
        found_names={},
        found_phone_numbers={},
        found_addresses={},
    )

def get_mock_website_info_with_multiple_data_types() -> WebsiteInfo:
    """Return a WebsiteInfo object with mixed data types."""
    return WebsiteInfo(
        found_urls={"https://example.com", "https://example.com/contact"},
        found_emails={
            "support@example.com": "https://example.com",
            "info@example.com": "https://example.com/contact",
        },
        found_names={
            "Alice Johnson": "https://example.com",
        },
        found_phone_numbers={},
        found_addresses={
            "789 Oak Ave, New York, NY 10001": "https://example.com/contact",
        },
    )