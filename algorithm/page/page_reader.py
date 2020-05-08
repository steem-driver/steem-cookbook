# -*- coding:utf-8 -*-

import traceback

from goose3 import Goose
from goose3.text import StopWords, StopWordsChinese, StopWordsArabic, StopWordsKorean
from newspaper import Article

from algorithm.page.page_link import PageLink
from utils.logging.logger import logger


class PageReaderBase:

    def __init__(self, url, lang="en"):
        self.url = url
        self.lang = lang
        self.article = None

        self.text_property = "text"
        self.title_property = "title"
        self.authors_property = "authors"
        self.publish_date_property = "publish_date"
        self.html_property = "raw_html"
        self.dom_property = "doc"

    def _read(self):
        if self.article is None:
            if self.lang is None:
                self.article = Article(self.url)
            else:
                self.article = Article(self.url, language=self.lang)
            try:
                self.article.download()
                self.article.parse()
            except:
                logger.info("failed when loading article content for {}\nError: {}".format(self.url, traceback.format_exc()))
        return self.article

    def _get(self, key):
        article = self._read()
        if article is None:
            return None
        data = article.__getattribute__(key)
        return data

    def main_text(self):
        text = self._get(self.text_property)
        if len(text) == 0:
            logger.info("No content has been fetched for {}".format(self.url))
            return None
        return text

    def title(self):
        return self._get(self.title_property)

    def authors(self):
        authors = self._get(self.authors_property)
        if authors is None:
            authors = []
        site_authors = read_site_authors(self.url, self._get(self.dom_property))
        authors.extend(site_authors)
        return authors

    def publish_date(self):
        return self._get(self.publish_date_property)

    def html(self):
        return self._get(self.html_property)

    def page_title(self):
        dom_tree = self._get(self.dom_property)
        if dom_tree is not None:
            title = dom_tree.findtext(".//title")
            return title or ""
        return ""


class PageReaderNewspaper(PageReaderBase):

    def __init__(self, url, lang="en"):
        PageReaderBase.__init__(self, url=url, lang=lang)
        self.text_property = "text"
        self.title_property = "title"
        self.authors_property = "authors"
        self.publish_date_property = "publish_date"
        self.html_property = "html"
        # use "article_html" if only need the article's html
        self.dom_property = "clean_doc"

    def _read(self):
        if self.article is None:
            if self.lang is None:
                self.article = Article(self.url, fetch_images=False, request_timeout=10, keep_article_html=True)
            else:
                lang = (self.lang)[:2].lower()
                # ignore the images by default
                self.article = Article(self.url, language=lang, fetch_images=False, request_timeout=10, keep_article_html=True)
            try:
                self.article.download()
                self.article.parse()
            except:
                logger.info("failed when loading article content for {}\nError: {}".format(self.url, traceback.format_exc()))
        return self.article


class PageReaderGoose(PageReaderBase):

    def __init__(self, url, lang="en"):
        PageReaderBase.__init__(self, url=url, lang=lang)
        self.text_property = "cleaned_text"
        self.title_property = "title"
        self.authors_property = "authors"
        self.publish_date_property = "publish_date"
        self.html_property = "raw_html"
        self.dom_property = "doc"

        if lang is None:
            self.g = Goose()
        else:
            lang = lang[:2].lower()
            if lang == "en":
                self.g = Goose()
            else:
                if lang == "zh":
                    stopwords_class = StopWordsChinese
                elif lang == "ko":
                    stopwords_class = StopWordsKorean
                elif lang == "ar":
                    stopwords_class = StopWordsArabic
                self.g = Goose({'stopwords_class': stopwords_class})


    def _read(self):
        if self.article is None:
            try:
                self.article = self.g.extract(url=self.url)
            except:
                logger.info("failed when loading article content for {}\nError: {}".format(self.url, traceback.format_exc()))
        return self.article


def find_element_text(dom_tree, path):
    elements = dom_tree.findall(path)
    if elements and len(elements) > 0:
        return [elements[0].text.strip()]
    return []

def read_site_authors(url, dom_tree):
    if url is not None and dom_tree is not None:
        u = PageLink(url)
        if u.has_hostname("publish0x.com"):
            path = ".//div[@class='row summary']/div/a"
            elements = dom_tree.findall(path)
            if elements and len(elements) > 0:
                for e in elements:
                    name = e.get("href")
                    if name and len(name) > 2 and name[:2] == "/@":
                        return [e.text.strip()]
        elif u.has_hostname("medium.com"):
            return find_element_text(dom_tree, ".//div[@class='u-paddingBottom3']/a")
        elif u.has_hostname("cryptocoinpravda.com"):
            return find_element_text(dom_tree, ".//div[@id='block_author-rcl']//h3[@class='user-name']/a")
        elif u.has_hostname("linkedin.com"):
            return find_element_text(dom_tree, ".//div[@class='bottom-bar']//section/h3/a")
        elif u.has_hostname("jianshu.com"):
            return find_element_text(dom_tree, ".//div[@class='info']/span[@class='name']/a")
    return []


PageReader = PageReaderNewspaper

