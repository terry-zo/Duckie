import re
from html import unescape


import nltk
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tag.perceptron import PerceptronTagger
from nltk.tokenize import RegexpTokenizer
from unidecode import unidecode

import network
import requests
import asyncio

STOP = set(stopwords.words("english")) - {"most", "least"}
tokenizer = RegexpTokenizer(r"\w+")
tagger = PerceptronTagger()
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
           "Accept": "*/*",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate"}
GOOGLE_URL = "https://www.google.com/search?q={}&ie=utf-8&oe=utf-8&client=firefox-b-1-ab"


def find_keywords(words):
    """
    Returns the list of words given without stopwords.
    :param words: List of words
    :return: Words without stopwords
    """
    return [w for w in tokenizer.tokenize(words.lower()) if w not in STOP]


def find_nouns(text, num_words, reverse=False):
    tokens = word_tokenize(text)
    tags = [tag for tag in tagger.tag(tokens) if tag[1] != "POS"]

    tags = tags[:num_words] if not reverse else tags[-num_words:]

    nouns = []
    consecutive_nouns = []

    for tag in tags:
        tag_type = tag[1]
        word = tag[0]

        if "NN" not in tag_type and len(consecutive_nouns) > 0:
            nouns.append(" ".join(consecutive_nouns))
            consecutive_nouns = []
        elif "NN" in tag_type:
            consecutive_nouns.append(word)

    if len(consecutive_nouns) > 0:
        nouns.append(" ".join(consecutive_nouns))

    return nouns


def find_q_word_location(question_lower):
    for q_word in ["what", "when", "who", "which", "whom", "where", "why", "how"]:
        q_word_location = question_lower.find(q_word)
        if q_word_location != -1:
            return q_word_location


def get_google_links(page, num_results):
    soup = BeautifulSoup(page, "html.parser")
    results = soup.findAll("h3", {"class": "r"})

    links = []
    for r in results:
        url = r.find("a")
        if url is not None:
            links.append(url["href"])
    links = list(dict.fromkeys(links))  # Remove duplicates while preserving order

    return links[:num_results]


async def search_google(question, num_results):
    """
    Returns num_results urls from a google search of question.
    :param question: Question to search
    :param num_results: Number of results to return
    :return: List of length num_results of urls retrieved from the search
    """
    # Could use Google's Custom Search API here, limit of 100 queries per day
    # result = service.cse().list(q=question, cx=CSE_ID, num=num_results).execute()
    # return result["items"]
    print(GOOGLE_URL.format(question))
    page = await network.get_response(GOOGLE_URL.format(question), timeout=5, headers=HEADERS)
    return get_google_links(page, num_results)


async def multiple_search(questions, num_results):
    queries = list(map(GOOGLE_URL.format, questions))
    pages = await network.get_responses(queries, timeout=5, headers=HEADERS)
    link_list = [get_google_links(page, num_results) for page in pages]
    return link_list


def clean_html(html):
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"\n", " ", cleaned)
    cleaned = re.sub(r"\s\s+", " ", cleaned)

    return unidecode(unescape(cleaned.strip()))


async def get_clean_texts(urls, timeout=1.5, headers=HEADERS):
    responses = await network.get_responses(urls, timeout, headers)

    return [clean_html(r).lower() for r in responses]


class RS(object):

    def __init__(self, answer, question):
        self.question = question
        self.answer = answer
        self.solver = "RS"

    async def toll_google(self):
        page = await network.get_response(f"https://www.google.com/search?q={self.question}", timeout=2, headers=HEADERS)
        soup = BeautifulSoup(page, "html.parser")
        try:
            result = int(soup.find("div", {"id": "resultStats"}).text.split(" ")[1].replace(",", ""))
            self.result = result
        except:
            self.result = 0
        return self


class Wiki(object):

    def __init__(self, question, answer):
        self.url = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=true&redirects=true&format=json&exintro=1&titles={}"
        self.question = question
        self.answer = answer

    async def search(self):
        try:
            searchUrl = self.url.format("".join(c for c in self.answer.replace(" / ", "|") if (c.isalnum() or c is " " or c is "|")))
            with requests.Session() as s:
                json_reponse = s.get(searchUrl, timeout=1).json()
            pages = ["".join(e for e in page["extract"] if (e.isalnum() or e is " ")).lower() for page_id, page in json_reponse["query"]["pages"].items() if "extract" in page]
            question_list = [word.lower() for word, tag in nltk.tag.pos_tag(self.question.split(" ")) if tag == 'NNP' or tag == 'NNPS']
            print(question_list)
            counts = [page.count(question) for question in question_list for page in pages]
            self.count = sum(counts)
        except:
            self.count = 0
        return self
