from bs4 import BeautifulSoup
from unittest.mock import MagicMock, patch
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from website import (
    is_file_url,
    parse,
    parse_all,
    get_links_from_html_content,
    parse_for_names,
    parse_for_emails,
    WebsiteInfo,
    parse_for_phone_numbers,
)


class WebsiteTest(unittest.TestCase):
    """Test class for the website module.

    Methods to test:
        parse,
        parse_all,
        get_links_from_html_content,
        is_file_url,
        parse_for_emails
    """

    @patch("website.website.webdriver.Chrome")
    def test_parse(self, mock_chrome) -> None:
        """Test the parse method.

        Arguments:
            mock_chrome: Mocked Chrome WebDriver object
        """

        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver

        mock_driver.page_source = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
                <p>Contact us at contact@example.com</p>
            </body>
        </html>
        """

        website_url = "https://example.com"
        info = WebsiteInfo(
            found_urls=set(), found_emails={}, found_names={}, found_phone_numbers={}
        )
        result: WebsiteInfo = parse(website_url, info)

        self.assertIsInstance(result, WebsiteInfo)
        self.assertIn("https://example.com/page1", result.found_urls)
        self.assertIn("https://example.com/page2", result.found_urls)
        self.assertIn("contact@example.com", result.found_emails)
        self.assertEqual(
            result.found_emails["contact@example.com"], "https://example.com"
        )

        with self.assertRaises(AssertionError):
            parse("Invalid URL", info)

    @patch("website.website.parse")
    def test_parse_all(self, mock_parse) -> None:
        """Test the parse_all method.

        Arguments:
            mock_parse: Mocked parse method
        """

        mock_parse.side_effect = [
            WebsiteInfo(
                found_urls={
                    "https://example.com",
                    "https://example.com/page1",
                },
                found_emails={"email1@example.com": "https://example.com/page1"},
                found_names={},
                found_phone_numbers={},
            ),
            WebsiteInfo(
                found_urls={
                    "https://example.com",
                    "https://example.com/page1",
                    "https://example.com/page2",
                },
                found_emails={
                    "email1@example.com": "https://example.com/page1",
                    "email2@example.com": "https://example.com/page2",
                },
                found_names={},
                found_phone_numbers={},
            ),
            WebsiteInfo(
                found_urls={
                    "https://example.com",
                    "https://example.com/page1",
                    "https://example.com/page2",
                },
                found_emails={
                    "email1@example.com": "https://example.com/page1",
                    "email2@example.com": "https://example.com/page2",
                },
                found_names={"Szabó István": "https://example.com/page1"},
                found_phone_numbers={"+36123456789": "https://example.com/page1"},
            ),
            WebsiteInfo(
                found_urls={
                    "https://example.com",
                    "https://example.com/page1",
                    "https://example.com/page2",
                },
                found_emails={
                    "email1@example.com": "https://example.com/page1",
                    "email2@example.com": "https://example.com/page2",
                },
                found_names={},
                found_phone_numbers={"+36123456789": "https://example.com/page1"},
            ),
        ]

        result: WebsiteInfo = parse_all("https://example.com", 3)

        self.assertIsInstance(result, WebsiteInfo)
        self.assertEqual(len(result.found_urls), 3)
        self.assertIn("https://example.com/page1", result.found_urls)
        self.assertIn("https://example.com/page2", result.found_urls)

        self.assertIn("email1@example.com", result.found_emails)
        self.assertIn("email2@example.com", result.found_emails)
        self.assertEqual(
            result.found_emails["email1@example.com"], "https://example.com/page1"
        )
        self.assertEqual(
            result.found_emails["email2@example.com"], "https://example.com/page2"
        )

        result: WebsiteInfo = parse_all("https://example.com", 4)
        self.assertEqual(len(result.found_urls), 3)

        with self.assertRaises(AssertionError):
            parse_all("Invalid URL", 2)
            parse_all("https://example.com", 0)

    def test_get_links_from_html_content(self) -> None:
        """Test the get_links_from_html_content method."""

        html_content = """
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
        found_urls_empty: set[str] = set()
        found_urls: set[str] = {
            "https://example.com/page2",
            "https://example.com/page5",
        }
        content = BeautifulSoup(html_content, "html.parser")

        result: set[str] = get_links_from_html_content(
            "https://example.com", content, found_urls_empty
        )
        self.assertIsInstance(result, set, "The result should be a set.")

        self.assertIn("https://example.com", result)
        self.assertIn("https://example.com/page1", result)
        self.assertIn("https://example.com/page2", result)
        self.assertIn("https://example.com/site.php", result)
        self.assertIn("https://example.com/page3", result)
        self.assertIn("https://example.com/page4", result)
        self.assertNotIn("https://example.com/", result)
        self.assertNotIn("https://example.com/page1/", result)
        self.assertNotIn("https://example.com/page1/", result)
        self.assertNotIn("https://example.com/site.php/", result)
        self.assertNotIn(
            "https://example.com/file.pdf", result, "File should be ignored"
        )
        self.assertNotIn(
            "https://example.com/page3#content", result, "ID should be ignored"
        )
        self.assertNotIn(
            "https://example.com/page4#content", result, "ID should be ignored"
        )
        self.assertNotIn("https://example.com/#id", result, "ID should be ignored")

        result: set[str] = get_links_from_html_content(
            "https://example.com", content, found_urls
        )
        self.assertEqual(len(result), 7)

        with self.assertRaises(AssertionError):
            get_links_from_html_content("Invalid URL", content, found_urls)

    def test_is_file_url(self) -> None:
        """Test the is_file_url method."""

        url_testcases: dict[str, bool] = {
            "https://example.com": False,
            "https://example.com/test.pdf": True,
            "https://example.com/test/test": False,
            "https://example.com/test.php": False,
            "/test.php": False,
            "/test.pdf": True,
        }

        for url, expected in url_testcases.items():
            value: bool = is_file_url(url)
            self.assertEqual(value, expected)

    def test_parse_for_emails(self) -> None:
        """Test the parse_for_emails method."""

        html_content = """
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
        found_emails_empty: dict[str, str] = dict()
        found_emails: dict[str, str] = {
            "info@company.org": "https://example.com/page2",
        }
        content = BeautifulSoup(html_content, "html.parser")

        result: dict[str, str] = parse_for_emails(
            "https://example.com", content, found_emails_empty
        )
        self.assertIsInstance(result, dict, "The result should be a dictionary.")

        self.assertIn("info@company.org", result)
        self.assertEqual(result["info@company.org"], "https://example.com")
        self.assertIn("firstname.lastname@example.com", result)
        self.assertEqual(
            result["firstname.lastname@example.com"], "https://example.com"
        )
        self.assertIn("email@subdomain.example.com", result)
        self.assertEqual(result["email@subdomain.example.com"], "https://example.com")
        self.assertIn("1234567890@example.com", result)
        self.assertEqual(result["1234567890@example.com"], "https://example.com")
        self.assertNotIn("invalidemail@example", result)
        self.assertNotIn("invalidemail@-example.com", result)

        result: dict[str, str] = parse_for_emails(
            "https://example.com", content, found_emails
        )
        self.assertIn("info@company.org", result)
        self.assertEqual(result["info@company.org"], "https://example.com/page2")

        with self.assertRaises(AssertionError):
            parse_for_emails("Invalid URL", content, found_emails)

    def test_parse_for_names(self) -> None:
        """Test the parse_for_names method."""

        html_content = """
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
        found_names_empty: dict[str, str] = dict()
        found_names: dict[str, str] = {
            "John Doe": "https://example.com/page2",
        }
        content = BeautifulSoup(html_content, "html.parser")

        result: dict[str, str] = parse_for_names(
            "https://example.com", content, found_names_empty
        )
        self.assertIsInstance(result, dict, "The result should be a dictionary.")

        self.assertIn("John Doe", result)
        self.assertEqual(result["John Doe"], "https://example.com")
        self.assertIn("Jane Smith", result)
        self.assertEqual(result["Jane Smith"], "https://example.com")
        self.assertIn("Joseph Gordon-Levitt", result)
        self.assertEqual(result["Joseph Gordon-Levitt"], "https://example.com")
        self.assertIn("Connor McGregor", result)
        self.assertEqual(result["Connor McGregor"], "https://example.com")
        self.assertIn("Conan O'Brien", result)
        self.assertEqual(result["Conan O'Brien"], "https://example.com")

        self.assertNotIn("Invalid name", result)
        self.assertNotIn("Another Invalid Name", result)

        result: dict[str, str] = parse_for_names(
            "https://example.com", content, found_names
        )
        self.assertIn("John Doe", result)
        self.assertEqual(result["John Doe"], "https://example.com/page2")
        self.assertIn("Jane Smith", result)
        self.assertEqual(result["Jane Smith"], "https://example.com")

        with self.assertRaises(AssertionError):
            parse_for_names("Invalid URL", content, found_names)

    def test_parse_for_phone_numbers(self) -> None:
        """Test the parse_for_phone_numbers method."""

        html_content = """
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
        found_phone_numbers_empty: dict[str, str] = dict()
        found_phone_numbers: dict[str, str] = {
            "+44 20 7777 7777": "https://example.uk/page2",
        }
        content = BeautifulSoup(html_content, "html.parser")

        result: dict[str, str] = parse_for_phone_numbers(
            "https://example.hu", content, found_phone_numbers_empty
        )
        self.assertIsInstance(result, dict, "The result should be a dictionary.")

        self.assertIn("+36 30 123 4567", result)
        self.assertEqual(result["+36 30 123 4567"], "https://example.hu")
        self.assertIn("+36 20 987 6543", result)
        self.assertEqual(result["+36 20 987 6543"], "https://example.hu")
        self.assertIn("+36 70 123 4567", result)
        self.assertEqual(result["+36 70 123 4567"], "https://example.hu")
        self.assertIn("+36 30 555 6666", result)
        self.assertEqual(result["+36 30 555 6666"], "https://example.hu")
        self.assertIn("+36 30 111 2222", result)
        self.assertEqual(result["+36 30 111 2222"], "https://example.hu")
        self.assertIn("+44 20 1234 5678", result)
        self.assertEqual(result["+44 20 1234 5678"], "https://example.hu")
        self.assertEqual(len(result), 6)

        self.assertNotIn("36 30 555 6666", result)
        self.assertNotIn("+36 30 1111 2222", result)
        self.assertNotIn("06 30 111 2222", result)
        self.assertNotIn("020 8366 1177", result)

        result: dict[str, str] = parse_for_phone_numbers(
            "https://example.uk", content, found_phone_numbers
        )
        self.assertIn("+44 20 7777 7777", result)
        self.assertIn("+44 20 8366 1177", result)

        self.assertNotIn("+36 30 111 2222", result)
        self.assertNotIn("06 30 111 2222", result)

        with self.assertRaises(AssertionError):
            parse_for_phone_numbers("Invalid URL", content, found_phone_numbers)


if __name__ == "__main__":
    unittest.main()
