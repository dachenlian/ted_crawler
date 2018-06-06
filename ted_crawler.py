import re
import json
from pathlib import Path
from time import sleep

import requests
from pyquery import PyQuery as pq
from fake_useragent import UserAgent


LAST_PAGE_CSS = "#browse-results > div.results__pagination > div > a:nth-child(13)"
TALK_LIST_CSS = "#browse-results > div.row.row-sm-4up.row-lg-6up.row-skinny > div > div > div > div " \
                "> div.media__message"
TALK_DETAILS_REGEX = re.compile(r"(?P<name>.+)\n(?P<title>.+)\nPosted (?P<post_date>.+)( Rated (?P<tags>.+))?")
LANGUAGES_CSS = "#shoji > div.shoji__door > div > div.main.pages-main > div > div > div > " \
                      "div.col-lg-9.pages-content > div.row.row-xs-2up.row-sm-3up.row-lg-4up > div"

ua = UserAgent()
HEADERS = {'user-agent': ua.chrome}


class TedCrawler:
    def __init__(self):
        self.current_page_no = 0
        self.base_url = "https://www.ted.com/"
        self.page_url = "talks?page={}"
        self.transcript_url_base = "/transcript.json?language={}"
        self.current_page = self.get_next_page()
        self.last_page = self.get_last_page()
        self.languages = self.get_languages()
        self.bookmark = self.get_bookmark()
        self.bookmark_has_run = False
        self.transcripts = {}

    def get_languages(self):
        url = self.base_url + "participate/translate/our-languages"
        d = pq(requests.get(url, headers=HEADERS).text)
        languages = d(LANGUAGES_CSS)
        language_dict = {}
        for language in languages:
            d = pq(language)
            full_name = d.text().split('\n')[0]
            abbr_name = d.find('a').attr('href').split('=')[1]
            language_dict[full_name] = abbr_name
        return language_dict

    def get_last_page(self):
        last_page = self.current_page(LAST_PAGE_CSS).text()
        return int(last_page)

    def get_next_page(self):
        self.current_page_no += 1
        r = requests.get(self.base_url + self.page_url.format(self.current_page_no), headers=HEADERS).text
        next_page = pq(r)
        print(f"Checking page {self.current_page_no}...")
        self.current_page = next_page
        return next_page

    def get_talk_list(self):
        talk_list = self.current_page(TALK_LIST_CSS)
        return talk_list

    def get_talk_details(self, talk):
        talk = pq(talk)
        talk_link = talk.find('a').attr('href')
        results = {'talk_link': talk_link, 'transcripts': {}}
        details = TALK_DETAILS_REGEX.search(talk.text())
        results.update(details.groupdict())
        return results

    def get_subtitles(self, talk, *args):
        transcript_url = self.base_url + talk['talk_link'] + self.transcript_url_base
        if not args:
            raise TypeError("Please choose at least one language.")
        for language in args:
            language_code = self.languages.get(language, None)
            if language_code:
                transcript = requests.get(transcript_url.format(language_code), headers=HEADERS).json()

            else:
                language_code = language
                transcript = requests.get(transcript_url.format(language_code), headers=HEADERS).json()

            if transcript.get('status', None) == '404':
                    print(f"{language} not found.")
                    talk['transcripts'][language_code] = None
                    continue
            talk['transcripts'][language_code] = transcript

        return talk

    def create_bookmark(self, talk):
        if not self.bookmark_has_run:
            with open('bookmark.json', 'w', encoding='utf8') as fp:
                d = {'bookmark': talk['title']}
                print(f"Creating bookmark with title: {talk['title']}")
                json.dump(d, fp, indent=4, ensure_ascii=False)
        self.bookmark_has_run = True

    def get_bookmark(self):
        bookmark = Path("bookmark.json")
        if bookmark.is_file():
            print("Found bookmark.")
            with open('bookmark.json', 'r') as fp:
                bookmark = json.load(fp)
                return bookmark['bookmark']
        else:
            print("Bookmark not found.")

    def write_to_json(self, path_name='ted_transcripts.json'):
        with open(path_name, 'w', encoding='utf8') as fp:
            json.dump(self.transcripts, fp, indent=4, ensure_ascii=False)
            # self.transcripts = {}


if __name__ == "__main__":
    crawler = TedCrawler()
    counter = 1
    while crawler.current_page_no < crawler.last_page:
        crawler.get_next_page()
        talk_list = crawler.get_talk_list()
        for talk in talk_list:
            sleep(3)
            talk_details = crawler.get_talk_details(talk)
            # if crawler.bookmark == talk_details['title']:
            #     print("Encountered old video. Quitting...")
            #     break
            crawler.create_bookmark(talk_details)
            talk_details = crawler.get_subtitles(talk_details, 'zh-cn', 'zh-tw')
            crawler.transcripts[talk_details['title']] = talk_details
        # if crawler.current_page_no % 10 == 0:
        #     crawler.write_to_json(path_name=f"TED_transcripts_{counter}.json")
        #     counter += 1

    crawler.write_to_json(path_name=f"TED_transcripts_{counter}.json")











