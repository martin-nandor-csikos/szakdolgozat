from export_data import constants as Constants
from export_data.enums import ExportChoice, WebparserCsvHeaderText, ProfilesCsvHeaderText
from itertools import zip_longest
from rich.console import Console
from website import WebsiteInfo
import csv
import os

console = Console(log_path=False)

def export_webparser_data(info: WebsiteInfo):
    """Export data found during parsing to a csv file.
    Only export the data if the user confirms the export and provides valid file names.

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
            file_path = _get_export_path(Constants.RESULTS_WEBPARSER_FOLDER)
            file_name = _get_file_name(file_path)
            if file_name is not None:
                _export_webparser_data_to_csv(info, file_path, file_name)
            else:
                console.print("[red]Export cancelled.[/red]")

def export_profiles(profiles: dict[str, str]):
    """Export LinkedIn profiles to a csv file.
    Only export the data if the user confirms the export and provides valid file names.

    Arguments:
        profiles (dict): The LinkedIn profiles found during the parsing process
    """
    if not isinstance(profiles, dict):
        raise TypeError(f"Invalid profiles type. Expected type: dict, actual type: {type(profiles)}")
    
    if len(profiles) != 0:
        is_start_export = _get_export_confirmation()
        if is_start_export == True:
            file_path = _get_export_path(Constants.RESULTS_PROFILES_FOLDER)
            file_name = _get_file_name(file_path)
            if file_name is not None:
                _export_profiles_to_csv(profiles, file_path, file_name)
            else:
                console.print("[red]Export cancelled.[/red]")

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
            console.print("[red]Invalid input. Please enter 'y' for yes or 'n' for no: [/red]", end="")

    if export_choice == ExportChoice.NO_EXPORT.value:
        return False
    return True

def _get_export_path(results_folder_name: str) -> str:
    """Get the results folder path for exporting CSV files.
    Creates the results folder if it doesn't exist.
    
     Returns:
        str: The path to the results folder
    """
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    results_folder = os.path.join(root_path, results_folder_name)
        
    if not os.path.exists(results_folder):
        try:
            os.makedirs(results_folder)
        except Exception as e:
            console.print(f"[red]Failed to create results folder: {e}[/red]")
            raise
    
    return results_folder

def _get_file_name(path: str) -> str | None:
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

        if len(file_name) == 0:
            console.print("[red]Empty file name. Please enter a valid name: [/red]")
            error_occured = True

        if not isinstance(file_name, str):
            console.print("[red]Invalid type for name. Please enter a valid name: [/red]")
            error_occured = True

        if len(file_name) > Constants.MAX_FILE_NAME_LENGTH:
            console.print(f"[red]File name is too long. Please enter a shorter name (max {Constants.MAX_FILE_NAME_LENGTH} characters): [/red]")
            error_occured = True

        if " " in file_name:
            console.print("[red]Invalid name, name contains spaces. Please enter a name without spaces: [/red]")
            error_occured = True

        if not error_occured:
            break
    
    full_path = os.path.join(path, file_name + Constants.CSV_EXTENSION)
    if os.path.exists(full_path):
        overwrite_choice = _ask_overwrite_existing_file()
        if overwrite_choice == ExportChoice.NO_EXPORT:
            return None

    # Removing the csv extension from the file name if it has one
    if file_name.endswith(Constants.CSV_EXTENSION):
        file_name = os.path.splitext(file_name)[0]

    return file_name

def _ask_overwrite_existing_file() -> ExportChoice:
    """Ask the user if they want to overwrite an existing file with the same name.
        Returns:
            ExportChoice: The user's choice to overwrite the existing file or not
    """
    console.print("[yellow]A file with this name already exists in the provided path. " \
    "This file will be overwritten. Do you want to continue? (y/n): [/yellow]", end="")

    while True:
        overwrite_choice = input().strip().lower()
        if overwrite_choice in [ExportChoice.EXPORT.value, ExportChoice.NO_EXPORT.value]:
            break
        else:
            console.print("[red]Invalid input. Please enter 'y' for yes or 'n' for no: [/red]", end="")

    if overwrite_choice == ExportChoice.NO_EXPORT.value:
        return ExportChoice.NO_EXPORT
    return ExportChoice.EXPORT

def _export_webparser_data_to_csv(info: WebsiteInfo, file_path: str, file_name: str):
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
        full_path = os.path.join(file_path, file_name + Constants.CSV_EXTENSION)
        csv_file = None
        try:
            with open(full_path, mode='w', newline='', encoding=Constants.UTF8_ENCODING) as csv_file:
                columns = data_columns.keys()
                writer = csv.DictWriter(csv_file, fieldnames=columns, delimiter=Constants.CSV_DELIMITER, quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()

                # Unpack data column values to separate arguments for zip_longest
                for row_values in zip_longest(*data_columns.values(), fillvalue=""):
                    row = dict(zip(columns, row_values))
                    writer.writerow(row)

            console.print(f"[green]Export completed successfully to {file_path}/{file_name}{Constants.CSV_EXTENSION}[/green]")
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

def _export_profiles_to_csv(profiles: dict[str, str], file_path: str, file_name: str):
    """Export the website information to a CSV file.
    
     Args:
        profiles (dict[str, str]): The profiles information to export
        file_path (str): The file path to export the CSV file to
        file_name (str): The name of the CSV file
    """
    if not isinstance(profiles, dict):
        raise TypeError(f"Invalid profiles type. Expected type: dict, actual type: {type(profiles)}")
    if not isinstance(file_path, str):
        raise TypeError(f"Invalid file_path type. Expected type: str, actual type: {type(file_path)}")
    if not isinstance(file_name, str):
        raise TypeError(f"Invalid file_name type. Expected type: str, actual type: {type(file_name)}")
    
    if len(profiles) != 0:
        full_path = os.path.join(file_path, file_name + Constants.CSV_EXTENSION)
        csv_file = None
        try:
            with open(full_path, mode='w', newline='', encoding=Constants.UTF8_ENCODING) as csv_file:
                writer = csv.writer(csv_file, delimiter=Constants.CSV_DELIMITER, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow([ProfilesCsvHeaderText.NAME.value, ProfilesCsvHeaderText.LINKEDIN_PROFILE.value])

                for url, name in profiles.items():
                    writer.writerow([name, url])

            console.print(f"[green]Export completed successfully to {file_path}/{file_name}{Constants.CSV_EXTENSION}[/green]")
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
    if not isinstance(info, WebsiteInfo):
        raise TypeError(f"Invalid info type. Expected type: WebsiteInfo, actual type: {type(info)}")
    
    data_columns = dict()
    if info.found_names:
        data_columns[WebparserCsvHeaderText.NAMES.value] = [f"{name} ({url})" for name, url in info.found_names.items()]
    if info.found_emails:
        data_columns[WebparserCsvHeaderText.EMAILS.value] = [f"{email} ({url})" for email, url in info.found_emails.items()]
    if info.found_phone_numbers:
        data_columns[WebparserCsvHeaderText.PHONE_NUMBERS.value] = [f"{phone} ({url})" for phone, url in info.found_phone_numbers.items()]
    if info.found_addresses:
        data_columns[WebparserCsvHeaderText.ADDRESSES.value] = [f"{address} ({url})" for address, url in info.found_addresses.items()]

    return data_columns