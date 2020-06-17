# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
# import logging
from .log_ import logger
# logger = logging.getLogger(__name__)


class ItcastSpider(scrapy.Spider):
    name = 'itcast'
    allowed_domains = ['www.itcast.cn']
    start_urls = ['http://www.itcast.cn/channel/teacher.shtml']

    def parse(self, response):
        # soup = BeautifulSoup(response.text, "lxml")
        # ret = response.xpath("//div[@class='tea_con']//h3/text()").extract()
        tea_list = response.xpath("//div[@class='tea_con']//li")
        for li in tea_list:
            item = dict()
            item["name"] = li.xpath(".//h3/text()").extract_first()
            item["title"] = li.xpath(".//h4/text()").extract_first()
            logger.warning(item)
            yield item


# scrapy.utils.spider.log
