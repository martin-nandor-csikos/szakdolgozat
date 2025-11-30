from bs4 import BeautifulSoup
from .mock_data import *
from unittest.mock import patch
import unittest

from website import (
    parse,
    parse_all,
    get_sublinks,
    get_names,
    get_emails,
    WebsiteInfo,
    get_phone_numbers,
    get_addresses,
)

class WebsiteTest(unittest.TestCase):
    """Test class for the website module."""

    @patch("website.website.webdriver.Remote")
    def test_parse(self, mock_remote):
        mock_remote.return_value = get_mock_parse()
        website_url = "https://example.com"
        info = WebsiteInfo(set(), {}, {}, {}, {})
        result = parse(website_url, info)

        self.assertIsInstance(result, WebsiteInfo)
        self.assertIn("https://example.com/page1", result.found_urls)
        self.assertIn("https://example.com/page2", result.found_urls)
        self.assertIn("contact@example.com", result.found_emails)
        self.assertEqual(result.found_emails["contact@example.com"], "https://example.com")

        with self.assertRaises(ValueError):
            parse("Invalid URL", info)

    @patch("builtins.input", return_value="n")
    @patch("website.website.parse")
    def test_parse_all(self, mock_parse, mock_input):
        mock_parse.side_effect = get_mock_parse_all()

        result = parse_all("https://example.com", 1)
        self.assertIsInstance(result, WebsiteInfo)
        self.assertGreaterEqual(len(result.found_urls), 2)
        self.assertIn("https://example.com/page1", result.found_urls)
        self.assertIn("email1@example.com", result.found_emails)

        with self.assertRaises(ValueError):
            parse_all("Invalid URL", 2)
        with self.assertRaises(TypeError):
            parse_all("https://example.com", "not_an_int")
        with self.assertRaises(ValueError):
            parse_all("https://example.com", -1)

    def test_get_sublinks(self):
        html_content = get_html_content_sublinks()
        found_urls_empty = set()
        found_urls = {"https://example.com/page2", "https://example.com/page5"}
        content = BeautifulSoup(html_content, "html.parser")

        result = get_sublinks("https://example.com", content, found_urls_empty)
        self.assertIsInstance(result, set)
        self.assertIn("https://example.com", result)
        self.assertIn("https://example.com/page1", result)
        self.assertIn("https://example.com/page2", result)
        self.assertIn("https://example.com/site.php", result)
        self.assertIn("https://example.com/page3", result)
        self.assertIn("https://example.com/page4", result)
        self.assertNotIn("https://example.com/file.pdf", result)

        with self.assertRaises(ValueError):
            get_sublinks("Invalid URL", content, found_urls)
        with self.assertRaises(TypeError):
            get_sublinks("https://example.com", "not_bs4", found_urls)
        with self.assertRaises(TypeError):
            get_sublinks("https://example.com", content, "not_a_set")

    def test_get_emails(self):
        html_content = get_html_content_emails()
        found_emails_empty = {}
        found_emails = {"info@company.org": "https://example.com/page2"}
        content = BeautifulSoup(html_content, "html.parser")

        result = get_emails("https://example.com", content, found_emails_empty)
        self.assertIsInstance(result, dict)
        self.assertIn("info@company.org", result)
        self.assertEqual(result["info@company.org"], "https://example.com")
        self.assertIn("firstname.lastname@example.com", result)
        self.assertEqual(result["firstname.lastname@example.com"], "https://example.com")
        self.assertIn("email@subdomain.example.com", result)
        self.assertEqual(result["email@subdomain.example.com"], "https://example.com")
        self.assertIn("1234567890@example.com", result)
        self.assertEqual(result["1234567890@example.com"], "https://example.com")
        self.assertNotIn("invalidemail@example", result)
        self.assertNotIn("invalidemail@-example.com", result)

        with self.assertRaises(ValueError):
            get_emails("Invalid URL", content, found_emails)
        with self.assertRaises(TypeError):
            get_emails("https://example.com", "not_bs4", found_emails)
        with self.assertRaises(TypeError):
            get_emails("https://example.com", content, "not_a_dict")

    def test_get_names(self):
        html_content = get_html_content_names()
        found_names_empty = {}
        found_names = {"John Doe": "https://example.com/page2"}
        content = BeautifulSoup(html_content, "html.parser")

        result = get_names("https://example.com", content, found_names_empty)
        self.assertIsInstance(result, dict)
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

        with self.assertRaises(ValueError):
            get_names("Invalid URL", content, found_names)
        with self.assertRaises(TypeError):
            get_names("https://example.com", "not_bs4", found_names)
        with self.assertRaises(TypeError):
            get_names("https://example.com", content, "not_a_dict")

    def test_get_phone_numbers(self):
        html_content = get_html_content_phones()
        found_phone_numbers_empty = {}
        found_phone_numbers = {"+44 20 7777 7777": "https://example.uk/page2"}
        content = BeautifulSoup(html_content, "html.parser")

        result = get_phone_numbers("https://example.hu", content, found_phone_numbers_empty)
        self.assertIsInstance(result, dict)
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

        with self.assertRaises(ValueError):
            get_phone_numbers("Invalid URL", content, found_phone_numbers)
        with self.assertRaises(TypeError):
            get_phone_numbers("https://example.com", "not_bs4", found_phone_numbers)
        with self.assertRaises(TypeError):
            get_phone_numbers("https://example.com", content, "not_a_dict")

    def test_get_addresses(self):
        html_content = get_html_content_addresses()
        found_addresses_empty = {}
        content = BeautifulSoup(html_content, "html.parser")

        result = get_addresses("https://example.com", content, found_addresses_empty)
        self.assertIsInstance(result, dict)
        found = any("123 main" in addr and "springfield" in addr for addr in result)
        self.assertTrue(found)
        found = any("újfalu utca" in addr and "kecskemét" in addr for addr in result)
        self.assertTrue(found)

        with self.assertRaises(ValueError):
            get_addresses("Invalid URL", content, found_addresses_empty)
        with self.assertRaises(TypeError):
            get_addresses("https://example.com", "not_bs4", found_addresses_empty)
        with self.assertRaises(TypeError):
            get_addresses("https://example.com", content, "not_a_dict")

if __name__ == "__main__":
    unittest.main()
