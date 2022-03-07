#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urllib.request, urllib.parse, urllib.error

class TendaENSpider(Spider):
    name = "tenda_en"
    vendor = "tenda"
    allowed_domains = ["tendacn.com"]
    start_urls = ["http://www.tendacn.com/en/service/download-cata-11-1.html"]
    url = "http://www.tendacn.com/en/service/download-cata-11-{}.html"

    def parse(self, response):
        for firmware in response.xpath("//tr[@class='downtr js-row-detail ']"):
            link = firmware.xpath("./td[@class='dr_name']/a/@href").extract()[0]
            link_url = link.replace("//www", "http://www")
            date = firmware.xpath("./td[@class='dr_date hidden-xs']/text()").extract()[0]
            #self.logger.debug(link_url)
            #self.logger.debug(date)
            yield Request(
                url=link_url,
                meta={"date": date},
                callback=self.parse_product)

    def parse_product(self, response):
        download = response.xpath("//div[@class='downbtns']/a[@class='downhits']/@href").extract()[0]
        download_url = download.replace("//", "http://").replace(" ", "%20")
        dsp = response.xpath("//div[@class='downdes']/h1/text()").extract()[0]
        product = dsp.split("Firmware")[0]
        version = dsp.split("Firmware")[-1]
        self.logger.debug(download_url)
        self.logger.debug(product)
        self.logger.debug(version)
        self.logger.debug(response.meta["date"])

        item = FirmwareLoader(
            item=FirmwareImage(), response=response)
        item.add_value("version", version)
        item.add_value("url", download_url)
        item.add_value("product", product)
        item.add_value("vendor", self.vendor)
        item.add_value("date", response.meta["date"])
        yield item.load_item()
