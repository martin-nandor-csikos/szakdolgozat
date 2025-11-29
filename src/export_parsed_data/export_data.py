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
    is_start_export = _get_export_confirmation()
    if is_start_export == True:
        file_path = _get_export_path()
        file_name = _get_file_name()
        _export_to_csv(info, file_path, file_name)

def _get_export_confirmation() -> bool:
    """Ask the user for confirmation to export data to CSV.
    
     Returns:
        bool: True if user wants to export, False otherwise
    """
    while True:
        console.print(Constants.GET_EXPORT_CONFIRM_MSG, end="")
        export_choice = input().strip().lower()

        if export_choice in [ExportChoice.EXPORT.value, ExportChoice.NO_EXPORT.value]:
            break
        else:
            console.print("[red]Invalid input. Please enter 'y' for yes or 'n' for no.[/red]")

    if export_choice == ExportChoice.NO_EXPORT.value:
        return False
    return True

def _get_export_path() -> str:
    """Get the file path from the user to export the CSV file.
    
     Returns:
        str: The file path to export the CSV file to
    """
    while True:
        console.print(Constants.GET_EXPORT_PATH_MSG, end="")
        export_path = input().strip().lower()

        if isinstance(export_path, str) and os.path.exists(export_path):
            break
        else:
            console.print("[red]Invalid path. Please enter a valid path.[/red]")
    
    return export_path

def _get_file_name() -> str:
    """Get the file name from the user for the exported CSV file.
    
     Returns:
        str: The file name for the exported CSV file
    """
    while True:
        console.print(Constants.GET_FILE_NAME_MSG, end="") 
        file_name = input().strip().lower()

        if isinstance(file_name, str):
            break
        else:
            console.print("[red]Invalid type for name. Please enter a valid name.[/red]")
    
    # Removing the extension from the file name and storing only the name
    name_without_extension = os.path.splitext(file_name)[0]

    return name_without_extension

def _export_to_csv(info: WebsiteInfo, file_path: str, file_name: str):
    """Export the website information to a CSV file.
    
     Args:
        info (WebsiteInfo): The website information to export
        file_path (str): The file path to export the CSV file to
        file_name (str): The name of the CSV file
    """

    data_columns = _get_data_columns(info)
    try:
        full_path = os.path.join(file_path, f"{file_name}.csv")
        with open(full_path, mode='w', newline='', encoding='utf-8') as csv_file:
            columns = data_columns.keys()
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()

            for row_values in zip_longest(*data_columns.values(), fillvalue=""):
                row = dict(zip(columns, row_values))
                writer.writerow(row)

            csv_file.close()

        console.print(f"[green]Export completed successfully to {file_path}/{file_name}.csv[/green]")
    except Exception as e:
        console.print(f"[red]Failed to export data to CSV: {e}[/red]")

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