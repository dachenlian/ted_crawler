import re
import json

import requests
from pyquery import PyQuery as pq


LAST_PAGE_CSS = "#browse-results > div.results__pagination > div > a:nth-child(13)"
TALK_LIST_CSS = "#browse-results > div.row.row-sm-4up.row-lg-6up.row-skinny"
TALK_DETAILS_REGEX = re.compile(r"(?P<name>.+)\n(?P<title>.+)\nPosted (?P<post_date>.+)( Rated (?P<tags>.+))?")


class TedCrawler:
    def __init__(self):
        self.current_page = 1
        self.last_page = self.get_last_page()
        self.base_url = "https://www.ted.com/talks?page={}"
        self.bookmark = None

    def get_last_page(self):
        last_page = pq(LAST_PAGE_CSS).text()
        return int(last_page)

    def get_next_page(self):
        while self.current_page < self.last_page:
            r = requests.get(self.base_url.format(self.current_page)).text
            next_page = pq(r)
            yield next_page
            self.current_page += 1

    def get_talk_list(self):
        page = self.get_next_page()
        print(f"Checking page {self.current_page}...")
        talk_list = page(TALK_LIST_CSS)
        yield talk_list

    def get_talk_details(self):






