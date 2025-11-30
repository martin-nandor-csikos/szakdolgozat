from export_parsed_data import constants as Constants
from export_parsed_data.enums import ExportChoice, CsvHeaderText
from itertools import zip_longest
from rich.console import Console
from website import WebsiteInfo
import csv
import os

console = Console(log_path=False)

def export_data(info: WebsiteInfo):
    """Export data found during parsing to a csv file.
    Only export the data if the user confirms the export and provides valid path and file names.

    Arguments:
        info (WebsiteInfo): The information found during the parsing process
    """
    if not isinstance(info, WebsiteInfo):
        raise TypeError(f"Invalid info type. Expected type: WebsiteInfo, actual type: {type(info)}")
    
    # Only export if data has been found during parsing
    # Links don't count as data
    if info.has_data():
        is_start_export = _get_export_confirmation()
        if is_start_export == True:
            file_path = _get_export_path()
            file_name = _get_file_name(file_path)
            _export_to_csv(info, file_path, file_name)

def _get_export_confirmation() -> bool:
    """Ask the user for confirmation to export data to CSV.
    
     Returns:
        bool: True if user wants to export, False otherwise
    """
    console.print(Constants.GET_EXPORT_CONFIRM_MSG, end="")
    while True:
        export_choice = input().strip().lower()

        if export_choice in [ExportChoice.EXPORT.value, ExportChoice.NO_EXPORT.value]:
            break
        else:
            console.print("[red]Invalid input. Please enter 'y' for yes or 'n' for no: [/red]")

    if export_choice == ExportChoice.NO_EXPORT.value:
        return False
    return True

def _get_export_path() -> str:
    """Get the file path from the user to export the CSV file.
    
     Returns:
        str: The file path to export the CSV file to
    """
    console.print(Constants.GET_EXPORT_PATH_MSG, end="")
    while True:
        export_path = input().strip()
        error_occured = False

        if not isinstance(export_path, str):
            console.print("[red]Invalid type for path. Please enter a valid path: [/red]")
            error_occured = True

        if not os.path.exists(export_path):
            console.print("[red]Path not found. Please enter an existing path: [/red]")
            error_occured = True

        if not error_occured:
            break
    
    return export_path

def _get_file_name(path: str) -> str:
    """Get the file name from the user for the exported CSV file.
    
     Returns:
        str: The file name for the exported CSV file
    """
    if not isinstance(path, str):
        raise TypeError(f"Invalid file_path type. Expected type: str, actual type: {type(path)}")

    console.print(Constants.GET_FILE_NAME_MSG, end="")
    while True:
        file_name = input().strip()
        error_occured = False

        if file_name == "":
            console.print("[red]Empty file name. Please enter a valid name: [/red]")
            error_occured = True

        if not isinstance(file_name, str):
            console.print("[red]Invalid type for name. Please enter a valid name: [/red]")
            error_occured = True

        max_file_name_length = 50
        if len(file_name) > max_file_name_length:
            console.print("[red]File name is too long. Please enter a shorter name: [/red]")
            error_occured = True

        full_path = os.path.join(path, f"{file_name}.csv")
        if os.path.exists(full_path):
            console.print("[red]A file with this name already exists in the provided path. " \
            "Please enter a different name: [/red]")
            error_occured = True

        if " " in file_name:
            console.print("[red]Invalid name, name contains spaces. Please enter a valid name: [/red]")
            error_occured = True

        if not error_occured:
            break
    
    # Removing the csv extension from the file name if it has one
    if file_name.endswith(".csv"):
        file_name = os.path.splitext(file_name)[0]

    return file_name

def _export_to_csv(info: WebsiteInfo, file_path: str, file_name: str):
    """Export the website information to a CSV file.
    
     Args:
        info (WebsiteInfo): The website information to export
        file_path (str): The file path to export the CSV file to
        file_name (str): The name of the CSV file
    """
    if not isinstance(info, WebsiteInfo):
        raise TypeError(f"Invalid info type. Expected type: WebsiteInfo, actual type: {type(info)}")
    if not isinstance(file_path, str):
        raise TypeError(f"Invalid file_path type. Expected type: str, actual type: {type(file_path)}")
    if not isinstance(file_name, str):
        raise TypeError(f"Invalid file_name type. Expected type: str, actual type: {type(file_name)}")
    
    if info.has_data():
        data_columns = _get_data_columns(info)
        full_path = os.path.join(file_path, f"{file_name}.csv")
        csv_file = None
        try:
            with open(full_path, mode='w', newline='', encoding='utf-8') as csv_file:
                columns = data_columns.keys()
                writer = csv.DictWriter(csv_file, fieldnames=columns)
                writer.writeheader()

                # Unpack data column values to separate arguments for zip_longest
                for row_values in zip_longest(*data_columns.values(), fillvalue=""):
                    row = dict(zip(columns, row_values))
                    writer.writerow(row)

            console.print(f"[green]Export completed successfully to {file_path}/{file_name}.csv[/green]")
        except Exception as e:
            console.print(f"[red]Failed to export data to CSV: {e}[/red]")
            if csv_file is not None and os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception as delete_error:
                    console.print(f"[red]Failed to delete incomplete CSV file: {delete_error}[/red]")
        finally:
            if csv_file is not None and os.path.exists(full_path):
                csv_file.close()

def _get_data_columns(info: WebsiteInfo) -> dict[str, list[str]]:
    """Get the data columns from the WebsiteInfo object for CSV export.

    Arguments:
        info (WebsiteInfo): The website information to extract data from

    Returns:
        dict[str, list[str]]: A dictionary containing data columns for CSV export. Key: column name, Value: list of data entries
    """
    data_columns = dict()
    if info.found_names:
        data_columns[CsvHeaderText.NAMES.value] = [f"{name} ({url})" for name, url in info.found_names.items()]
    if info.found_emails:
        data_columns[CsvHeaderText.EMAILS.value] = [f"{email} ({url})" for email, url in info.found_emails.items()]
    if info.found_phone_numbers:
        data_columns[CsvHeaderText.PHONE_NUMBERS.value] = [f"{phone} ({url})" for phone, url in info.found_phone_numbers.items()]
    if info.found_addresses:
        data_columns[CsvHeaderText.ADDRESSES.value] = [f"{address} ({url})" for address, url in info.found_addresses.items()]

    return data_columns