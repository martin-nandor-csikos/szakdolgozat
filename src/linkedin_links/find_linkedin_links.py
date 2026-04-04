from linkedin_links import constants as Constants
from ddgs import DDGS
from rich.console import Console
import threading
import time

console = Console(log_path=False)

def fetch_links(company: str, profile_count: int) -> dict[str, str]:
    """Get the search links from the user input using DuckDuckGo.
    
     Returns:
        dict[str, str]: The dictionary of profile links and names. Key: url, Value: name
    """
    profiles = dict()
    search_query = f"\"{company}\" site:linkedin.com/in"

    stop_event = threading.Event()
    heartbeat_thread = threading.Thread(target=_result_count_heartbeat, args=(profiles, stop_event), daemon=True)
    heartbeat_thread.start()

    try:
        ddgs = DDGS()
        results = ddgs.text(search_query, max_results=profile_count, region=Constants.HU_REGION)
        
        for result in results:
            result_url = result['href']
            result_title = result['title']
            
            # Get the person's name from the title
            # Title is usually formatted as "Name - Company" or "Name - Title at Company"
            result_name = result_title.split(" - ")[0].strip()
            profiles[result_url] = result_name

        if len(profiles) < profile_count:
            console.print(f"[yellow]Only {len(profiles)} profile links were found.[/yellow]")
    finally:
        stop_event.set()
        heartbeat_thread.join(timeout=1)

    print(profiles)
    return profiles

def _result_count_heartbeat(profiles: dict, stop_event: threading.Event):
    """Print the count of found results every 10 seconds."""
    while not stop_event.is_set():
        time.sleep(Constants.HEARTBEAT_INTERVAL_SECONDS)
        console.print(f"{len(profiles)} profile links found so far...")