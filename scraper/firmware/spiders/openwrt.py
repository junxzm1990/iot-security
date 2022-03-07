from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error
import logging

class OpenWRTSpider(Spider):
    name = "openwrt"
    allowed_domains = ["downloads.openwrt.org"]
    start_urls = ["http://downloads.openwrt.org/"]

    def parse(self, response):
        for link in response.xpath("//a"):
            text = link.xpath("text()").extract_first()
            href = link.xpath("@href").extract_first()

            if text is None and href == "/":
                # <a href="/"><em>(root)</em></a>
                continue
            if "19.07.7" in href or "18.06.9" in href:
                version = href.split("/")[1]
                self.logger.debug(href)
                self.logger.debug(version)
                yield Request(
                    url=urllib.parse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    meta={"version":version},
                    callback=self.parse_url)

    def parse_url(self, response):
        body = response.xpath("./body")
        filename = body.xpath(".//h2[1]/text()").extract()
        if len(filename) > 0:
            target = body.xpath("./p/b/text()").extract()[0]
            #self.logger.debug(filename)
            for file_row in body.xpath("./table[1]//tr"):
                file_url = file_row.xpath("./td[@class='n']/a/@href").extract()
                date_raw = file_row.xpath("./td[@class='d']/text()").extract()
                if len(file_url) > 0:
                    tmp = date_raw[0].split(" ")
                    date = tmp[1] + "/" + tmp[2] + "/" + tmp[4]
                    #self.logger.debug(file_url)
                    #self.logger.debug(date)
                    #self.logger.debug(target)
                    #self.logger.debug(response.meta["version"])
                    if any(file_url[0].endswith(x) for x in [".bin", ".img", ".img.gz"]):
                        self.logger.debug("Mark")
                        item = FirmwareLoader(
                            item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                        item.add_value("version", response.meta["version"])
                        item.add_value("url", urllib.parse.urljoin(response.url, file_url[0]))
                        item.add_value("date", date)
                        item.add_value("product", target)
                        item.add_value("vendor", self.name)
                        item.add_value("build", file_url[0])
                        yield item.load_item()

        else:
            for href in body.xpath(".//table//a/@href").extract():
                yield Request(
                    url=urllib.parse.urljoin(response.url, href),
                    headers={"Referer": response.url},
                    meta={"version":response.meta["version"]},
                    callback=self.parse_url)
        

        '''
        for link in response.xpath("//a"):
            text = link.xpath("text()").extract_first()
            href = link.xpath("@href").extract_first()

            if text is None and href == "/":
                # <a href="/"><em>(root)</em></a>
                continue

            if ".." in href:
                continue
            elif href.endswith('/'):
                if "package/" not in text:
                    product = "%s-%s" % (response.meta["product"], text[0: -1]) if "product" in response.meta else text[0: -1]
                    
                    yield Request(
                        url=urllib.parse.urljoin(response.url, href),
                        headers={"Referer": response.url},
                        meta={"version": response.meta[
                            "version"], "product": product},
                        callback=self.parse_url)
            ## comment out .elf .fdt .imx .chk .trx .imx

        '''
