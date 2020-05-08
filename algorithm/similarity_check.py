# -*- coding:utf-8 -*-

from algorithm.page.page_language import PageLanguage
from algorithm.page.page_reader import PageReader

from algorithm.match.tf_idf import TFIDFComparator


SIMILARITY_THRESHOLD = 0.9


class SimilarityCheck:

    def __init__(self, target, source, lang=None):
        self.target = target
        self.source = source

        if lang is None:
            sample = self.target["body"]
            self.lang = PageLanguage(sample).detect()
        else:
            self.lang = lang

    def _read_text(self, obj):
        if "body" in obj and obj["body"] \
            and "title" in obj and obj["title"]:
            return obj
        elif "url" in obj and obj["url"]:
            reader = PageReader(url=obj["url"], lang=self.lang)
            if not "body" in obj or obj["body"] is None:
                obj["body"] = reader.main_text()
            if not "title" in obj or obj["title"] is None:
                obj["title"] = reader.title()
            # if not "authors" in obj or obj["authors"] is None:
            #     obj["authors"] = reader.authors()
        return obj

    def compare(self, comparator=TFIDFComparator):
        target = self._read_text(self.target)
        source = self._read_text(self.source)

        if target["title"] == source["title"] or target["body"] == source["body"]:
            simialrity = 1.0
        elif target["body"] and source["body"]:
            simialrity = comparator(text1=target["body"],
                                         text2=source["body"]).compare()
        else:
            simialrity = -1.0

        return float(simialrity)
