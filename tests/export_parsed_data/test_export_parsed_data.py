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
    get_mock_website_info_empty,
    get_mock_website_info_with_multiple_data_types,
)

class ExportDataTest(unittest.TestCase):
    """Test class for the export_parsed_data module."""

    @classmethod
    def setUpClass(cls):
        """Set up the csv_export_files directory if doesn't exist."""
        cls.csv_export_dir = os.path.join(
            os.path.dirname(__file__), "csv_export_files"
        )
        os.makedirs(cls.csv_export_dir, exist_ok=True)

    def _get_timestamped_filename(self, test_name: str) -> str:
        """Generate filename containing timestamp of current time."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{test_name}_{timestamp}"
    
    @patch('builtins.input', side_effect=['invalid input', '1', 'y'])
    def test_get_export_confirmation_invalid_then_valid_yes(self, mock_input):
        """Test getting export confirmation with invalid inputs followed by valid 'yes' response."""
        result = _get_export_confirmation()
        self.assertTrue(result)

    @patch('builtins.input', side_effect=['invalid_input', 'x', 'n'])
    def test_get_export_confirmation_invalid_then_valid_no(self, mock_input):
        """Test getting export confirmation with invalid inputs followed by valid 'no' response."""
        result = _get_export_confirmation()
        self.assertFalse(result)

    @patch('builtins.input', side_effect=['', 'invalid', 'Y'])
    def test_get_export_confirmation_case_insensitive(self, mock_input):
        """Test getting export confirmation is case insensitive."""
        result = _get_export_confirmation()
        self.assertTrue(result)

    @patch('builtins.input')
    def test_get_export_path_valid(self, mock_input):
        """Test getting export path with valid input."""
        mock_input.return_value = self.csv_export_dir
        result = _get_export_path()
        self.assertEqual(result, self.csv_export_dir)

    @patch('builtins.input', side_effect=['/invalid/path', tempfile.gettempdir()])
    def test_get_export_path_invalid_then_valid(self, mock_input):
        """Test getting export path with invalid path followed by valid path."""
        result = _get_export_path()
        # Should eventually return a valid path
        self.assertTrue(os.path.exists(result))

    def test_get_file_name_with_invalid_type_path(self):
        """Test get_file_name with invalid path type."""
        with self.assertRaises(TypeError):
            _get_file_name(123)

    @patch('builtins.input', return_value='My_Export_File')
    def test_get_file_name_normal_filename(self, mock_input):
        """Test getting a normal file name."""
        result = _get_file_name(self.csv_export_dir)
        self.assertEqual(result, 'My_Export_File')

    @patch('builtins.input', side_effect=['test file with spaces', 'test_file_no_spaces'])
    def test_get_file_name_with_spaces_then_valid(self, mock_input):
        """Test getting file name with spaces then valid name."""
        result = _get_file_name(self.csv_export_dir)
        self.assertEqual(result, 'test_file_no_spaces')

    @patch('builtins.input', return_value='file_with.multiple.dots.csv')
    def test_get_file_name_with_multiple_dots(self, mock_input):
        """Test getting file name with multiple dots (should only strip .csv extension)."""
        result = _get_file_name(self.csv_export_dir)
        self.assertEqual(result, 'file_with.multiple.dots')

    @patch('builtins.input', side_effect=['', 'valid_name'])
    def test_get_file_name_empty_then_valid(self, mock_input):
        """Test getting file name with empty input followed by valid name."""
        result = _get_file_name(self.csv_export_dir)
        self.assertEqual(result, 'valid_name')

    def test_get_file_name_existing_file(self):
        """Test getting file name when file already exists."""
        # Create a test file
        existing_file = os.path.join(self.csv_export_dir, "existing_file.csv")
        with open(existing_file, 'w') as f:
            f.write("test")
        
        try:
            with patch('builtins.input', side_effect=['existing_file', 'new_file']):
                result = _get_file_name(self.csv_export_dir)
                self.assertEqual(result, 'new_file')
        finally:
            # Clean up
            if os.path.exists(existing_file):
                os.remove(existing_file)

    @patch('builtins.input', side_effect=['x' * 51, 'x' * 50])
    def test_get_file_name_too_long_then_valid(self, mock_input):
        """Test getting file name with name that's too long, then valid name."""
        result = _get_file_name(self.csv_export_dir)
        self.assertEqual(result, 'x' * 50)

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

    @patch('csv.DictWriter.writerow', side_effect=Exception("Write error"))
    def test_export_to_csv_deletes_file_on_exception(self, mock_writerow):
        """Test that CSV file is deleted if an exception occurs during export."""
        website_info = get_mock_website_info_with_all_data()
        file_name = self._get_timestamped_filename("test_delete_on_exception")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        # File should be deleted if an exception occurred
        self.assertFalse(os.path.exists(csv_path))

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_export_to_csv_handles_file_open_error(self, mock_open):
        """Test that _export_to_csv handles errors when opening file."""
        website_info = get_mock_website_info_with_all_data()
        file_name = self._get_timestamped_filename("test_open_error")

        # Should not raise an exception
        try:
            _export_to_csv(website_info, self.csv_export_dir, file_name)
        except Exception as e:
            self.fail(f"_export_to_csv raised {type(e).__name__} unexpectedly!")

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        # File should not exist if open failed
        self.assertFalse(os.path.exists(csv_path))

    @patch('csv.DictWriter.writeheader', side_effect=IOError("Write header error"))
    def test_export_to_csv_deletes_file_on_write_header_error(self, mock_writeheader):
        """Test that CSV file is deleted if an error occurs during writeheader."""
        website_info = get_mock_website_info_with_all_data()
        file_name = self._get_timestamped_filename("test_delete_on_header_error")

        _export_to_csv(website_info, self.csv_export_dir, file_name)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        # File should be deleted if an exception occurred
        self.assertFalse(os.path.exists(csv_path))

    @patch('os.remove', side_effect=Exception("Cannot delete file"))
    def test_export_to_csv_handles_deletion_error(self, mock_remove):
        """Test that _export_to_csv handles errors when deleting incomplete file."""
        website_info = get_mock_website_info_with_all_data()
        file_name = self._get_timestamped_filename("test_deletion_error")

        # Patch writerow to trigger an exception
        with patch('csv.DictWriter.writerow', side_effect=Exception("Write error")):
            # Should not raise an exception even if deletion fails
            try:
                _export_to_csv(website_info, self.csv_export_dir, file_name)
            except Exception as e:
                self.fail(f"_export_to_csv raised {type(e).__name__} unexpectedly!")

    @patch('export_parsed_data.export_data._get_export_confirmation', return_value=True)
    @patch('export_parsed_data.export_data._get_export_path')
    @patch('export_parsed_data.export_data._get_file_name')
    def test_export_data_full_flow(self, mock_file_name, mock_path, mock_confirmation):
        """Test the full export_data flow."""
        file_name = self._get_timestamped_filename("test_export")
        mock_file_name.return_value = file_name
        mock_path.return_value = self.csv_export_dir
        website_info = get_mock_website_info_with_all_data()
        initial_file_count = len([f for f in os.listdir(self.csv_export_dir) if f.endswith('.csv')])

        export_data(website_info)

        csv_path = os.path.join(self.csv_export_dir, f"{file_name}.csv")
        self.assertTrue(os.path.exists(csv_path))
        final_file_count = len([f for f in os.listdir(self.csv_export_dir) if f.endswith('.csv')])
        file_count_difference = final_file_count - initial_file_count
        self.assertEqual(file_count_difference, 1)

if __name__ == "__main__":
    unittest.main()