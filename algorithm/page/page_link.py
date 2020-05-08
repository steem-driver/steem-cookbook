# -*- coding:utf-8 -*-

import re
from urllib.parse import urlparse, urlunparse


FILE_SUFFIXES = ["txt", "pdf", "xml", "doc", "docx", "xls", "xlsx", "csv"]
TRANSLATION_HOSTS = ["translate.google.com", "www.excel.blue"]
VIDEO_HOSTS = ["youtube.com", "bitchute.com", "crypto-video.ru"]

NON_NAME_CHARS_REGEX = r"[^a-zA-Z0-9]+"
NON_NAME_CHARS_IN_URL_REGEX = r"[^a-zA-Z0-9\/\:]+"

DEFAULT_SCHEME = "https"


class PageLink:

    def __init__(self, url):
        self.url = url
        self.u = urlparse(url)

    def _is_file_ext(self, path):
        ext = path.split(".")[-1].lower()
        if ext in FILE_SUFFIXES:
            return True
        return False

    def is_file(self):
        return self._is_file_ext(self.u.path) or self._is_file_ext(self.url)

    def is_translation_service(self):
        hostname = self.u.hostname
        for host in TRANSLATION_HOSTS:
            if host in hostname:
                return True
        return False

    def is_video(self):
        hostname = self.u.hostname
        for host in VIDEO_HOSTS:
            if host in hostname:
                return True
        return False

    def _author_match(self, str1, str2):
        if str1 and str2 and len(str1) > 0 and len(str2) > 0:
            if str1 in str2 or str2 in str1:
                return True
        return False

    def has_author(self, author):
        # check whether the author is in the path except the last one
        author = author.lower()
        if self.url[-1] == "/":
            url = self.url[:-1]
        page_location = "/".join(self.url.split("/")[:-1]).lower()
        page_location = re.sub(NON_NAME_CHARS_IN_URL_REGEX, "", page_location)
        if author in page_location:
            return True

        if "medium.com" in self.u.hostname:
            path = self.u.path
            if path[0] == "/":
                path = path[1:]
            medium_author = path.split("/")[0].lower()
            author1 = re.sub(NON_NAME_CHARS_REGEX, "", author)
            author2 = re.sub(NON_NAME_CHARS_REGEX, "", medium_author)
            if self._author_match(author1, author2):
                return True
            return False

        return False

    def get_author_source(self, author):
        if self.has_author(author):
            author = re.sub(NON_NAME_CHARS_REGEX, "", author.lower())

            if self.url[-1] == "/":
                url = self.url[:-1]
            paths = self.url.split("/")[:-1]
            for i in range(0, len(paths)):
                path = re.sub(NON_NAME_CHARS_REGEX, "", paths[i].lower())
                if self._author_match(author, path):
                    source = "/".join(paths[:i+1])
                    return source
        return None

    def get_location(self):
        return self.u.scheme + "://" + self.u.hostname

    def match(self, url):
        another = PageLink(url)
        return self.u.hostname == another.u.hostname and self.u.path == another.u.path

    def _normalize(self, url):
        has_scheme = ":" in url[:7]
        is_universal_scheme = url.startswith("//")
        if not has_scheme and not is_universal_scheme:
            url = "//" + url

        u = urlparse(url)
        u = u._replace(scheme=DEFAULT_SCHEME)
        hostname = re.sub(r"^www\.", "", u.hostname)
        u = u._replace(netloc=hostname)
        return urlunparse(u)

    def has_prefix(self, prefix):
        if prefix is None or len(prefix) == 0:
            return False
        return self._normalize(prefix) in self._normalize(self.url)

    def has_hostname(self, host):
        hostname = self.u.hostname
        if host:
            if host.lower() in hostname.lower():
                return True
        return False
