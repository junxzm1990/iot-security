#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import re
import urllib.request, urllib.parse, urllib.error
import logging

class NetcoreSpider(Spider):
    name = "netcore"
    allowed_domains = ["netcoretec.com"]
    url_base = "http://www.netcoretec.com/portal/list/index/id/12.html?id=12&page="
    start_urls = []
    for i in range(13):
        full_url = url_base + str(i+1)
        start_urls.append(full_url)
    #start_urls = ["http://www.netcoretec.com/portal/list/index/id/12.html?id=12&page=2"]
    product_url = 'http://www.netcoretec.com/upload/'
    firmware_url = "http://www.netcoretec.com/"

    def parse(self, response):
        th = False
        self.logger.debug("WTF")
        self.logger.debug(response.url)
        for tr in response.xpath("//div[@class='load_list']//tr"):
            if not th:
                th = True
                continue
            info = tr.xpath("//a[@class='btn']/@href")
            for link in info:
                #self.logger.debug(type(link))
                link_url=urllib.parse.urljoin(self.firmware_url, link.extract())
                yield Request(
                    url=link_url,
                    headers={"Referer": response.url},
                    #meta={"date": date,
                    #      "description": title,
                    #      "product": product,
                    #      },
                    callback=self.parse_product)
            
    def parse_product(self, response):
        url = response.xpath("//input[@class='load_check check_item']/@file_url").extract()
        date = response.xpath("//div[@class='tag']/span/text()").extract()[1]
        product = response.xpath("//div[@class='title']/text()").extract()[0]
        file_url=urllib.parse.urljoin(self.product_url, url[0])
        self.logger.debug(file_url)
        self.logger.debug(product)
        self.logger.debug(date)

        item = FirmwareLoader(item=FirmwareImage(), response=response)
        item.add_value("date", date)
        #item.add_value("description",  response.meta['description'])
        item.add_value("url",  file_url)
        item.add_value("product", product)
        item.add_value("vendor", self.name)
        yield item.load_item()
