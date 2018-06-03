import re
import json
from pathlib import Path

import requests
from pyquery import PyQuery as pq


LAST_PAGE_CSS = "#browse-results > div.results__pagination > div > a:nth-child(13)"
TALK_LIST_CSS = "#browse-results > div.row.row-sm-4up.row-lg-6up.row-skinny > div > div > div > div " \
                "> div.media__message"
TALK_DETAILS_REGEX = re.compile(r"(?P<name>.+)\n(?P<title>.+)\nPosted (?P<post_date>.+)( Rated (?P<tags>.+))?")
LANGUAGES_CSS = "#shoji > div.shoji__door > div > div.main.pages-main > div > div > div > " \
                      "div.col-lg-9.pages-content > div.row.row-xs-2up.row-sm-3up.row-lg-4up > div"


class TedCrawler:
    def __init__(self):
        self.current_page = 1
        self.last_page = self.get_last_page()
        self.base_url = "https://www.ted.com/"
        self.page_url = "talks?page={}"
        self.transcript_url_base = "transcript.json?language={}"
        self.languages = self.get_languages()
        self.bookmark = self.get_bookmark()
        self.bookmark_has_run = False
        self.transcripts = {}

    def get_languages(self):
        url = self.base_url + "participate/translate/our-languages"
        d = pq(requests.get(url).text)
        languages = d(LANGUAGES_CSS)
        language_dict = {}
        for language in languages:
            d = pq(language)
            full_name = d.text().split('\n')[0]
            abbr_name = d.find('a').attr('href').split('=')[1]
            language_dict[full_name] = abbr_name
        return language_dict

    def get_last_page(self):
        last_page = pq(LAST_PAGE_CSS).text()
        return int(last_page)

    def get_next_page(self):
        r = requests.get(self.base_url + self.page_url.format(self.current_page)).text
        next_page = pq(r)
        yield next_page
        self.current_page += 1

    def get_talk_list(self, page):
        print(f"Checking page {self.current_page}...")
        talk_list = page(TALK_LIST_CSS)
        yield talk_list

    def get_talk_details(self, talk):
        talk_link = pq(talk).find('a').attr('href')
        results = {'talk_link': talk_link, 'transcripts': {}}
        details = TALK_DETAILS_REGEX.search(talk)
        yield results.update(details.groupdict())

    def get_subtitles(self, talk, *args):
        transcript_url = self.base_url + talk['talk_link'] + self.transcript_url_base
        for language in args:
            language_code = self.languages.get(language, None)
            if language_code:
                transcript = requests.get(transcript_url.format(language_code)).json()
                talk['transcripts'][language_code] = transcript
            else:
                transcript = requests.get(transcript_url.format(language)).json()
                if transcript['status'] == '404':
                    print(f"{language} not found.")
                    continue

        yield talk

    def create_bookmark(self, talk):
        if not self.bookmark_has_run:
            with open('bookmark.json', 'w', encoding='utf8') as fp:
                d = {'bookmark': talk['title']}
                print(f"Creating bookmark with title: {talk['title']}")
                json.dump(d, fp, indent=4, ensure_ascii=False)

    def get_bookmark(self):
        bookmark = Path("bookmark.json")
        if bookmark.is_file():
            print("Found bookmark.")
            with open('bookmark.json', 'r') as fp:
                return json.load(fp)
        else:
            print("Bookmark not found.")

    def write_to_json(self, path_name='transcripts.json'):
        with open(path_name) as fp:
            json.dump(self.transcripts, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    crawler = TedCrawler()











