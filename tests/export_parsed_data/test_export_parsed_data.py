import os
import unittest
import tempfile
import csv
from unittest.mock import patch
from datetime import datetime

from export_parsed_data import export_data
from export_parsed_data.export_data import _get_export_confirmation, _get_export_path, _get_file_name, _export_to_csv
from .mock_data import (
    get_mock_website_info_with_all_data,
    get_mock_website_info_with_names_only,
    get_mock_website_info_with_emails_only,
    get_mock_website_info_empty,
    get_mock_website_info_with_multiple_data_types,
)

class ExportDataTest(unittest.TestCase):
    """Test class for the export_parsed_data module."""

    @classmethod
    def setUpClass(cls):
        """Set up the csv export files directory."""
        cls.csv_export_dir = os.path.join(
            os.path.dirname(__file__), "csv_export_files"
        )
        os.makedirs(cls.csv_export_dir, exist_ok=True)

    def _get_timestamped_filename(self, test_name: str) -> str:
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{test_name}_{timestamp}"

    def test_export_to_csv_with_all_data(self):
        """Test exporting CSV with all data types populated."""
        website_info = get_mock_website_info_with_all_data()
        file_name = self._get_timestamped_filename("test_all_data")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))

        # Verify CSV contents
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 0)
            # Check that all column headers are present
            self.assertIsNotNone(reader.fieldnames)

    def test_export_to_csv_with_names_only(self):
        """Test exporting CSV with only names data."""
        website_info = get_mock_website_info_with_names_only()
        file_name = self._get_timestamped_filename("test_names_only")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))

        # Verify CSV has only Names column
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.assertEqual(len(reader.fieldnames), 1)
            self.assertIn("Names (found at link)", reader.fieldnames)

    def test_export_to_csv_with_emails_only(self):
        """Test exporting CSV with only emails data."""
        website_info = get_mock_website_info_with_emails_only()
        file_name = self._get_timestamped_filename("test_emails_only")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))

        # Verify CSV has only Emails column
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.assertEqual(len(reader.fieldnames), 1)
            self.assertIn("Emails (found at link)", reader.fieldnames)

    def test_export_to_csv_with_empty_data(self):
        """Test exporting CSV with empty data."""
        website_info = get_mock_website_info_empty()
        file_name = self._get_timestamped_filename("test_empty_data")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        # File should not be created for empty data
        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertFalse(os.path.exists(csv_path))

    def test_export_to_csv_with_multiple_data_types(self):
        """Test exporting CSV with mixed data types."""
        website_info = get_mock_website_info_with_multiple_data_types()
        file_name = self._get_timestamped_filename("test_mixed_data")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))

        # Verify CSV contents
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 0)
            # Should have 3 columns (Names, Emails, Addresses)
            self.assertEqual(len(reader.fieldnames), 3)
            self.assertIn("Names (found at link)", reader.fieldnames)
            self.assertIn("Emails (found at link)", reader.fieldnames)
            self.assertIn("Addresses (found at link)", reader.fieldnames)

    def test_export_to_csv_creates_file(self):
        """Test that CSV file is created at the correct path."""
        website_info = get_mock_website_info_with_all_data()
        file_name = self._get_timestamped_filename("test_file_creation")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(os.path.isfile(csv_path))

    def test_export_to_csv_invalid_path(self):
        """Test exporting to an invalid path."""
        website_info = get_mock_website_info_with_all_data()
        invalid_path = "/invalid/nonexistent/path"
        file_name = self._get_timestamped_filename("test_file")

        # Should not raise an exception, but should handle gracefully
        try:
            _export_to_csv(website_info, invalid_path, file_name)
        except Exception as e:
            self.fail(f"_export_to_csv raised {type(e).__name__} unexpectedly!")

    @patch('builtins.input', return_value='y')
    def test_get_export_confirmation_yes(self, mock_input):
        """Test getting export confirmation with 'yes' response."""
        result = _get_export_confirmation()
        self.assertTrue(result)

    @patch('builtins.input', return_value='n')
    def test_get_export_confirmation_no(self, mock_input):
        """Test getting export confirmation with 'no' response."""
        result = _get_export_confirmation()
        self.assertFalse(result)

    @patch('builtins.input')
    def test_get_export_path_valid(self, mock_input):
        """Test getting export path with valid input."""
        mock_input.return_value = self.csv_export_dir
        result = _get_export_path()
        self.assertEqual(result, self.csv_export_dir)

    @patch('builtins.input', side_effect=['/invalid/path', tempfile.gettempdir()])
    def test_get_export_path_invalid_then_valid(self, mock_input):
        """Test getting export path with invalid then valid input."""
        result = _get_export_path()
        # Should eventually return a valid path
        self.assertTrue(os.path.exists(result))

    @patch('builtins.input', return_value='results')
    def test_get_file_name_simple(self, mock_input):
        """Test getting file name with simple input."""
        result = _get_file_name()
        self.assertEqual(result, "results")

    @patch('builtins.input', return_value='results_2025_07_05')
    def test_get_file_name_with_underscores(self, mock_input):
        """Test getting file name with underscores."""
        result = _get_file_name()
        self.assertEqual(result, "results_2025_07_05")

    @patch('builtins.input', return_value='results.csv')
    def test_get_file_name_with_extension(self, mock_input):
        """Test getting file name with .csv extension (should strip it)."""
        result = _get_file_name()
        self.assertEqual(result, "results")

    @patch('export_parsed_data.export_data._get_export_confirmation', return_value=True)
    @patch('export_parsed_data.export_data._get_export_path')
    @patch('export_parsed_data.export_data._get_file_name')
    def test_export_data_full_flow(self, mock_file_name, mock_path, mock_confirmation):
        """Test the full export_data flow."""
        file_name = self._get_timestamped_filename("test_export")
        mock_file_name.return_value = file_name
        mock_path.return_value = self.csv_export_dir
        website_info = get_mock_website_info_with_all_data()

        export_data(website_info)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))

    @patch('export_parsed_data.export_data._get_export_confirmation', return_value=False)
    def test_export_data_user_cancels(self, mock_confirmation):
        """Test export_data when user declines to export."""
        website_info = get_mock_website_info_with_all_data()
        initial_file_count = len([f for f in os.listdir(self.csv_export_dir) if f.endswith('.csv')])

        export_data(website_info)

        # No new files should be created
        final_file_count = len([f for f in os.listdir(self.csv_export_dir) if f.endswith('.csv')])
        self.assertEqual(initial_file_count, final_file_count)

if __name__ == "__main__":
    unittest.main()