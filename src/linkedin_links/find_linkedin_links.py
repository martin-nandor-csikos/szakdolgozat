from globals.enums import DataRegion
from linkedin_links import constants as Constants
from ddgs import DDGS
from rich.console import Console

console = Console(log_path=False)

def fetch_links(company: str, profile_count: int, region: DataRegion) -> dict[str, str]:
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
    if not isinstance(region, DataRegion):
        raise TypeError(f"Invalid region type. Expected type: DataRegion, actual type: {type(region)}")
    
    console.log(f"Searching for LinkedIn profile links")

    profiles = dict()

    match region.value.lower():
        case DataRegion.HUNGARY.value:
            search_region = Constants.HU_REGION
        case DataRegion.UNITED_STATES.value:
            search_region = Constants.US_REGION
        case _:
            search_region = Constants.UK_REGION

    if region == DataRegion.HUNGARY:
        search_query = f"\"{company}\" {Constants.LINKEDIN_SITE_HU} {Constants.EXCLUDED_PAGES}"
    else:
        search_query = f"\"{company}\" {Constants.LINKEDIN_SITE_ALL} {Constants.EXCLUDED_PAGES}"
    profiles = _get_profile_results(search_query, profile_count, search_region)

    console.log(f"[green]Searching completed[/green]")
    if len(profiles) < profile_count:
        console.print(f"[yellow]Only {len(profiles)} profile links were found.[/yellow]")

    return profiles

def _get_profile_results(search_query: str, profile_count: int, search_region: str) -> dict[str, str]:
    """Get the search results from DuckDuckGo based on the search query, profile count and search region.
    
    Arguments:
        search_query (str): The search query to use
        profile_count (int): The maximum number of profiles to fetch
        search_region (str): The region to use for the search

    Returns:
        dict[str, str]: The dictionary of profile links and names. Key: url, Value: name
    """
    if not isinstance(search_query, str):
        raise TypeError(f"Invalid search_query type. Expected type: str, actual type: {type(search_query)}")
    if not isinstance(profile_count, int):
        raise TypeError(f"Invalid profile_count type. Expected type: int, actual type: {type(profile_count)}")
    if not isinstance(search_region, str):
        raise TypeError(f"Invalid search_region type. Expected type: str, actual type: {type(search_region)}")
    
    ddgs = DDGS()
    results = ddgs.text(search_query, max_results=profile_count*2, region=search_region)
    profiles = dict()

    for result in results:
        result_url = result['href']
        result_title = result['title']
        
        # Filter to only LinkedIn profile URLs
        if 'linkedin' not in result_url or '/in/' not in result_url:
            continue
        
        # Get the person's name from the title
        # Title is usually formatted as "Name - Company" or "Name - Title at Company"
        result_name = result_title.strip()
        if " -" in result_name:
            result_name = result_name.split(" -")[0].strip()
        # Em dash
        if " –" in result_name:
            result_name = result_name.split(" –")[0].strip()
        if "," in result_name:
            result_name = result_name.split(",")[0].strip()

        profiles[result_url] = result_name

        if len(profiles) >= profile_count:
            break

    return profiles