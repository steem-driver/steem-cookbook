# -*- coding:utf-8 -*-

import requests

from steem.settings import settings
from steem.collector import query
from steem.comment import SteemComment
from algorithm.similarity_check import SimilarityCheck
from utils.logging.logger import logger

# hive info
HIVE_HOST = "https://hive.blog"

class DoubleSent:

    def __init__(self, account, source, days=7):
        self.account = account
        self.source = source
        self.days = days

    def find_double_sent(self):
        if self._same_link_on_hive():
            logger.info("post with same author / permlink found: {}".format(self.source.get_url(HIVE_HOST)))
            return True

        posts = self.fetch_posts(self.days)
        if posts and len(posts) > 0:
            for post in posts:
                similarity = self._measure_similarity(post)
                if similarity > 0.7:
                    logger.info("similar posts found: {}; sim = {}".format(post.authorperm, similarity))
                    return post
        return None

    def fetch_posts(self, days):
        settings.set_hive_node()
        posts = query({
            "mode": "post",
            "account": self.account,
            "days": days
        })
        settings.set_steem_node()
        return posts

    def _same_link_on_hive(self):
        r = requests.get(self.source.get_url(HIVE_HOST))
        if r.ok:
            return True
        else:
            return False

    def _measure_similarity(self, post):
        target = SteemComment(comment=post)
        logger.info("measure {}".format(post.title))

        return SimilarityCheck(
          {
              "title": self.source.title(),
              "body": self.source.get_text_body()
          }, {
              "title": target.title(),
              "body": target.get_text_body()
          }).compare()

