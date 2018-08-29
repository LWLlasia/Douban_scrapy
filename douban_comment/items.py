# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanCommentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_name = scrapy.Field()
    movie_id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    type = scrapy.Field()
    comment = scrapy.Field()
    comment_type = scrapy.Field()
    time = scrapy.Field()
    good = scrapy.Field()
    source = scrapy.Field()
    pass
