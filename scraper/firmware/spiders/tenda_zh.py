#coding:utf-8
#note: 官网bug，升级软件栏目只能打开一页
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import json
import urllib.request, urllib.parse, urllib.error

class TendaZHSpider(Spider):
    name = "tenda_zh"
    vendor = "tenda"
    allowed_domains = ["www.tenda.com.cn"]
    start_urls = ["http://www.tenda.com.cn/service/download-cata-11.html"]
    base_url = "http://www.tenda.com.cn/{}"

    def parse(self, response):
        for firmware in response.xpath("//tr[@class='downtr     ']"):
            link = firmware.xpath("./td[@class='dr_name']/a/@href").extract()[0]
            link_url = link.replace("//", "https://")
            date = firmware.xpath("./td[@class='dr_date hidden-xs']/text()").extract()[1]
            self.logger.debug(link_url)
            self.logger.debug(date)
            if "down.tenda" in link_url:
                continue
                #name = firmware.xpath("./td[@class='dr_name']/a/text()").extract()[0]
                #product = name.split("升级软件")[0]
                #version = name.split("升级软件")[-1]
                #self.logger.debug("Mark")
                #self.logger.debug(product)
                #self.logger.debug(version)
            else:
                yield Request(
                    url=link_url,
                    meta={"date": date},
                    callback=self.parse_product)


    def parse_product(self, response):
        download = response.xpath("//td[@class='col-right']/a[@class='btnxz btndown downhits']/@href").extract()[0]
        download_url = download.replace("//", "https://").replace(" ", "%20")
        dsp = response.xpath("//td[@class='col-right']/p/text()").extract()
        product = dsp[0]
        version = dsp[1]
        #self.logger.debug(download_url)
        #self.logger.debug(dsp)
        #self.logger.debug(version)
        #self.logger.debug(response.meta["date"])

        item = FirmwareLoader(
            item=FirmwareImage(), response=response)
        item.add_value("version", version)
        item.add_value("url", download_url)
        item.add_value("product", product)
        item.add_value("vendor", self.vendor)
        item.add_value("date", response.meta["date"])
        yield item.load_item()
