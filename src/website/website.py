from bs4 import BeautifulSoup
import re


class Website:

    def __init__(self, driver, webpage):
        self.__driver = driver
        self.__webpage = webpage

        self.__found_urls = []
        self.__visited_urls = []
        self.__number_of_pages_visited = 1
        self.__found_emails = []

    @property
    def driver(self):
        return self.__driver

    @driver.setter
    def driver(self, new_driver):
        self.__driver = new_driver

    @property
    def webpage(self):
        return self.__webpage

    @webpage.setter
    def webpage(self, new_webpage):
        self.__webpage = new_webpage

    @property
    def found_urls(self):
        return self.__found_urls

    @found_urls.setter
    def found_urls(self, new_found_urls: list):
        self.__found_urls = new_found_urls

    @property
    def visited_urls(self):
        return self.__visited_urls

    @visited_urls.setter
    def visited_urls(self, new_visited_urls: list):
        self.__visited_urls = new_visited_urls

    @property
    def number_of_pages_visited(self):
        return self.__number_of_pages_visited

    @number_of_pages_visited.setter
    def number_of_pages_visited(self, new_number_of_pages_visited: int):
        self.__number_of_pages_visited = new_number_of_pages_visited

    @property
    def number_of_pages_visited(self):
        return self.__number_of_pages_visited

    @number_of_pages_visited.setter
    def number_of_pages_visited(self, new_number_of_pages_visited):
        self.__number_of_pages_visited = new_number_of_pages_visited

    def parse_links(self, number_of_pages_to_visit: int) -> None:
        content = self.__get_site_content()
        main_site_request_html = BeautifulSoup(content, "html.parser")
        self.__get_links_from_html(main_site_request_html)

        # self.parse_for_emails(main_site_request_html)

        self.visited_urls.append(self.webpage)
        print(self.found_urls)

        for found_url in self.found_urls:
            if (
                found_url not in self.visited_urls
                and number_of_pages_to_visit != self.number_of_pages_visited
            ):
                self.number_of_pages_visited += 1
                self.parse_links(number_of_pages_to_visit)

    def __get_site_content(self) -> str:
        self.driver.get(self.webpage)
        content = self.driver.page_source
        return content

    def __get_links_from_html(self, request_html: BeautifulSoup) -> None:
        for link_tag in request_html.find_all("a"):
            print(link_tag)
            if not link_tag.has_attr("href"):
                continue

            href = link_tag.attrs["href"]

            if href.startswith("/"):
                found_url = self.webpage + href

                if found_url not in self.found_urls and ".pdf" not in found_url:
                    self.found_urls.append(found_url)

    # def parse_for_emails(self, site_request_html) -> None:
    #     email_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    #     emails = re.findall(email_regex, site_request_html.decode())

    #     for email in emails:
    #         if email not in self.found_emails:
    #             self.found_emails.append(email)

    #     print(self.found_emails)
