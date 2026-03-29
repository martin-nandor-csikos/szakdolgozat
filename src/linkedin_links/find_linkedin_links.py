from export_parsed_data import constants as Constants
from googlesearch import search
from itertools import permutations
from rich.console import Console
from website import WebsiteInfo
import time

console = Console(log_path=False)

def get_links(names: list[str], company: str):
    """Get the Google search links from the user input.
    
     Returns:
        list[str]: The list of Google search links provided by the user
    """
    links = list()
    for name in names:
        # Create different combinations of the name to increase the chances
        # Append every combination with OR in the query
        name_combinations = _get_name_combinations(name)
        name_combinations_in_query = ""
        for name_combination in name_combinations:
            if name_combination is not name_combinations[-1]:
                name_combinations_in_query += f"\"{name_combination}\" OR "
            else:
                name_combinations_in_query += f"\"{name_combination}\""

        search_query = f"\"{company}\" {name_combinations_in_query} site:linkedin.com/in"

        # Add checking name in title
        results = search(search_query, advanced=True)
        for url in results:
            links.append(url)

        time.sleep(3)


    print(links)
    return links

def _get_name_combinations(name: str) -> list[str]:
    """Get different combinations of the given name to increase the chances of finding the LinkedIn profile.

     Returns:
        list[str]: The list of name combinations
    """
    parts = name.split()
    all_orders = [" ".join(p) for p in permutations(parts)]
    return all_orders