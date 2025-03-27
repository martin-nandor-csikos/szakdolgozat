import sys
from selenium import webdriver
from website.website import Website


def __init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    return webdriver.Chrome(options=options)


def main():
    webdriver = __init_driver()
    site = sys.argv[1]
    number_of_pages_to_visit = sys.argv[2]
    website = Website(driver=webdriver, webpage=site)
    website.parse_links(number_of_pages_to_visit)
    webdriver.quit()


if __name__ == "__main__":
    main()
