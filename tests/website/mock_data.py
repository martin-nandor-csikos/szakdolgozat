from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))
from website.models import WebsiteInfo

def get_mock_parse():
    mock_driver = MagicMock()
    mock_driver.page_source = get_html_content_basic()
    return mock_driver

def get_mock_parse_all():
    return [
        WebsiteInfo(
            found_urls={"https://example.com", "https://example.com/page1"},
            found_emails={"email1@example.com": "https://example.com/page1"},
            found_names={},
            found_phone_numbers={},
            found_addresses={},
        ),
        WebsiteInfo(
            found_urls={"https://example.com", "https://example.com/page1", "https://example.com/page2"},
            found_emails={
                "email1@example.com": "https://example.com/page1",
                "email2@example.com": "https://example.com/page2",
            },
            found_names={},
            found_phone_numbers={},
            found_addresses={},
        ),
    ]

def get_html_content_basic():
    return HTML_CONTENT_BASIC

def get_html_content_sublinks():
    return HTML_CONTENT_SUBLINKS

def get_html_content_emails():
    return HTML_CONTENT_EMAILS

def get_html_content_names():
    return HTML_CONTENT_NAMES

def get_html_content_phones():
    return HTML_CONTENT_PHONES

def get_html_content_addresses():
    return HTML_CONTENT_ADDRESSES

HTML_CONTENT_BASIC = """
<html>
    <body>
        <a href="/page1">Page 1</a>
        <a href="https://example.com/page2">Page 2</a>
        <p>Contact us at contact@example.com</p>
    </body>
</html>
"""

HTML_CONTENT_SUBLINKS = """
<html>
    <body>
        <a href="https://example.com">Main page</a>
        <a href="/page1">Site link</a>
        <a href="#id">ID</a>
        <a href="https://example.com/page2">Absolute URL link</a>
        <a href="/file.pdf">PDF File</a>
        <a href="/site.php">PHP Site</a>
        <a href="/page3#content">Site link with ID</a>
        <a href="https://example.com/page4#content">Absolute URL link with ID</a>
    </body>
</html>
"""

HTML_CONTENT_EMAILS = """
<html>
    <body>
        <p>info@company.org</p>
        <p>firstname.lastname@example.com</p>
        <p>email@subdomain.example.com</p>
        <p>1234567890@example.com</p>
        <p>invalidemail@example</p>
        <p>invalidemail@-example.com</p>
    </body>
</html>
"""

HTML_CONTENT_NAMES = """
<html>
    <body>
        <p>      John Doe      </p>
        <h1> Random text lorem ipsum
        Jane Smith
        Lorem ipsum dolor sit amet
        </h1>
        <p>Joseph Gordon-Levitt</p>
        <p>Connor McGregor</p>
        <p>Conan O'Brien</p>
        <h2>Invalid name</h2>
        <a>Another Invalid Name</a>
    </body>
</html>
"""

HTML_CONTENT_PHONES = """
<html>
    <body>
        <p>Number with spaces: +36 30 123 4567</p>
        <p>Number with dashes: +36-20-987-6543</p>
        <p>Number with dash and parenthesis: +36 (70) 123-4567</p>
        <p>Number without plus: 36305556666</p>
        <p>Too long number: +36-30-1111-2222</p>
        <p>Hungarian national number: 06 30 111 2222</p>
        <p>UK international number: +44 20 1234 5678</p>
        <p>UK national number: 020 8366 1177</p>
    </body>
</html>
"""

HTML_CONTENT_ADDRESSES = """
<html>
    <body>
        <p>123 Main St, Springfield, IL 62704</p>
        <p>Some random text</p>
        <p>6000 Kecskemét, Újfalu utca 31.</p>
    </body>
</html>
"""