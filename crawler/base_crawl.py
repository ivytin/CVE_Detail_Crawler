#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'


class BaseCrawl(object):
    """Base class of website crawler.

    all crawlers must extend this class and override
    craw() function.

    Attributes:
        websites: crawling website page target
        items: part of this page need to crawl
    """

    def __init__(self, websites, items):
        self.websites = websites
        self.items = items
