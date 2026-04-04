from globals.enums import DataLanguage
from linkedin_links import constants as Constants
from ddgs import DDGS
from rich.console import Console
import threading
import time

console = Console(log_path=False)

def fetch_links(company: str, profile_count: int, language: str) -> dict[str, str]:
    """Get the search links from the user input using DuckDuckGo.
    
     Returns:
        dict[str, str]: The dictionary of profile links and names. Key: url, Value: name
    """
    if not isinstance(company, str):
        raise TypeError(f"Invalid company type. Expected type: str, actual type: {type(company)}")
    if not isinstance(profile_count, int):
        raise TypeError(f"Invalid profile_count type. Expected type: int, actual type: {type(profile_count)}")
    if profile_count < 1:
        raise ValueError("The number of profiles to fetch must be at least 1 or more")
    if not isinstance(language, str):
        raise TypeError(f"Invalid language type. Expected type: str, actual type: {type(language)}")
    
    profiles = dict()

    stop_event = threading.Event()
    heartbeat_thread = threading.Thread(target=_result_count_heartbeat, args=(profiles, stop_event), daemon=True)
    heartbeat_thread.start()

    if language == DataLanguage.HUNGARIAN.value:
        search_language = Constants.HU_REGION
    else:
        search_language = Constants.US_REGION

    try:
        search_query = f"\"{company}\" {Constants.LINKEDIN_SITE}"
        profiles = _get_profile_results(search_query, profile_count, search_language)
    finally:
        stop_event.set()
        heartbeat_thread.join(timeout=1)

    if len(profiles) < profile_count:
        console.print(f"[yellow]Only {len(profiles)} profile links were found.[/yellow]")

    print(profiles)
    return profiles

def _get_profile_results(search_query: str, profile_count: int, search_language: str) -> dict[str, str]:
    """Get the search results from DuckDuckGo based on the search query, profile count and search language.
    
    Arguments:
        search_query (str): The search query to use
        profile_count (int): The maximum number of profiles to fetch
        search_language (str): The region to use for the search

    Returns:
        dict[str, str]: The dictionary of profile links and names. Key: url, Value: name
    """
    if not isinstance(search_query, str):
        raise TypeError(f"Invalid search_query type. Expected type: str, actual type: {type(search_query)}")
    if not isinstance(profile_count, int):
        raise TypeError(f"Invalid profile_count type. Expected type: int, actual type: {type(profile_count)}")
    if not isinstance(search_language, str):
        raise TypeError(f"Invalid search_language type. Expected type: str, actual type: {type(search_language)}")
    
    ddgs = DDGS()
    results = ddgs.text(search_query, max_results=profile_count, region=search_language)
    profiles = dict()

    for result in results:
        result_url = result['href']
        result_title = result['title']
        
        # Get the person's name from the title
        # Title is usually formatted as "Name - Company" or "Name - Title at Company"
        result_name = result_title.split(" - ")[0].strip()
        profiles[result_url] = result_name
    
    return profiles

def _result_count_heartbeat(profiles: dict, stop_event: threading.Event):
    """Print the count of found results every 10 seconds."""
    if not isinstance(profiles, dict):
        raise TypeError(f"Invalid profiles type. Expected type: dict, actual type: {type(profiles)}")
    if not isinstance(stop_event, threading.Event):
        raise TypeError(f"Invalid stop_event type. Expected type: threading.Event, actual type: {type(stop_event)}")
    
    while not stop_event.is_set():
        time.sleep(Constants.HEARTBEAT_INTERVAL_SECONDS)
        console.print(f"{len(profiles)} profile links found so far...")