# Update on 03/02/2020
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import os
import urllib.request, urllib.parse, urllib.error

class TomatoShibbySpider(Spider):
    name = "tomato-shibby"
    allowed_domains = ["tomato.groov.pl"]
    start_urls = ["http://tomato.groov.pl/download"]
    download_path = "https://tomato.groov.pl"
    def parse(self, response):
        for link in response.xpath("//table//tr"):
            if not link.xpath("./td[2]/a"):
                continue
            
            text = link.xpath("./td[2]/a/text()").extract()[0]
            href = link.xpath("./td[2]//@href").extract()[0]

            if ".." in href or "Exp" in href:
                continue
            elif href.endswith('/'):
                build = response.meta.get("build", None)
                product = response.meta.get("product", None)

                if not product:
                    product = text
                elif not build:
                    build = text.replace("build", "")

                yield Request(
                url=urllib.parse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    meta={"build": build, "product": product},
                    callback=self.parse)
            elif any(href.endswith(x) for x in [".bin", ".fdt", ".imx", ".chk", ".trx"]):
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%Y-%m-%d"])
                item.add_value("build", response.meta["build"])
                item.add_value("url", urllib.parse.urljoin(self.download_path, href))
                item.add_value("version", link.xpath("./td[2]//a/text()").extract()[0])
                item.add_value("date", link.xpath("./td[3]/text()").extract()[0].split(".")[0])
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                #self.logger.debug(urllib.parse.urljoin(self.download_path, href))
                #self.logger.debug(response.meta["product"])
                #self.logger.debug(link.xpath("./td[3]/text()").extract()[0])
                #self.logger.debug(link.xpath("./td[2]/a/text()").extract()[0].split(".")[0])
                yield item.load_item()
