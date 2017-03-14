# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def split_back_splant(text):
    """
    去除反斜杠，并以反斜杠分割为数组
    :param text:
    :return: list
    """
    text = text.replace(' ', '')
    return text.split(':')[-1].split('/')


def str_to_digit(text):
    """
    :param text:
    :return:  float
    """
    return float(text)


def str_to_datetime(datetime_str):
    for mnt in ('%Y-%m-%d', '%Y', '%Y-%m'):
        try:
            return datetime.strptime(datetime_str.strip(), mnt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def trim_suffix(text):
    # 去除‘(中国大陆)之类的后缀
    return text.split('(')[0]


def strip_all_spaces(text):
    return text.replace(' ', '')


class MovieLoader(ItemLoader):

    default_output_processor = TakeFirst()

    name_in = MapCompose(remove_tags, strip_all_spaces)

    actors_in = MapCompose(remove_tags)
    actors_out = MapCompose(split_back_splant)

    rate_in = MapCompose(str_to_digit)

    screenwriters_in = MapCompose(remove_tags, strip_all_spaces)
    screenwriters_out = MapCompose(split_back_splant)

    directors_in = MapCompose(remove_tags, strip_all_spaces)
    directors_out = MapCompose(split_back_splant)

    genre_in = MapCompose(remove_tags)
    genre_out = MapCompose(split_back_splant)

    language_in = MapCompose(remove_tags, split_back_splant)

    release_date_in = MapCompose(remove_tags, trim_suffix, str_to_datetime)

    length_in = MapCompose(str_to_digit)


class Movie(scrapy.Item):

    url = scrapy.Field()
    name = scrapy.Field()
    rate = scrapy.Field()
    directors = scrapy.Field()
    screenwriters = scrapy.Field()
    actors = scrapy.Field()
    genre = scrapy.Field()
    language = scrapy.Field()
    release_date = scrapy.Field()
    length = scrapy.Field()
