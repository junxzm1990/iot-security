from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error
import logging

class HikvisionSpider(Spider):
    name = "hikvision"
    allowed_domains = ["hikvisioneurope.com"]
    start_urls = ["http://www.hikvisioneurope.com/uk/portal/?dir=portal/Product%20Firmware"]

    def parse(self, response):
            
        folder_name = response.xpath('//table[@id="datatable-checkbox"]/tbody/tr/td[1]/@data-name').extract()
        next_url = response.xpath('//table[@id="datatable-checkbox"]/tbody/tr/td[1]/@data-href').extract()
        for i in range(len(folder_name)):
            if ".." not in folder_name[i]:
                url=urllib.parse.urljoin(response.url, next_url[i])
                #self.logger.debug(folder_name)
                #self.logger.debug(url)
                #self.logger.debug("CNM")
            
                yield Request(
                    url=urllib.parse.urljoin(response.url, next_url[i]),
                    headers={"Referer": response.url},
                    meta={"product": folder_name[i]},
                        #meta={"version": FirmwareLoader.find_version_period(text)},
                    callback=self.parse_url)
            
    def parse_url(self, response):
        folder_name = response.xpath('//table[@id="datatable-checkbox"]/tbody/tr/td[1]/@data-name').extract()
        next_url = response.xpath('//table[@id="datatable-checkbox"]/tbody/tr/td[1]/@data-href').extract()
        date = response.xpath('//table[@id="datatable-checkbox"]/tbody/tr/td[3]').extract()
        for i in range(len(folder_name)):
            if ".." not in folder_name[i] and "upgrading" not in folder_name[i]:
                url=urllib.parse.urljoin(response.url, next_url[i])
                product = response.meta["product"] + "/" + folder_name[i]
                #self.logger.debug(product)
                #self.logger.debug(url)
                #self.logger.debug(date[i])
                #self.logger.debug("CNM2")
                if any(url.endswith(x) for x in [".rar", ".zip", ".ZIP", "bin", ".apk"]):
                    self.logger.debug("END")
                    self.logger.debug(folder_name[i])
                    self.logger.debug(url)
                    item = FirmwareLoader(item=FirmwareImage(), response=response)
                    date_str = date[i].replace("<td>", "").replace("</td>","")
                    self.logger.debug(date_str)
                    item.add_value("url", url)
                    item.add_value("product", product)
                    item.add_value("vendor", "hikvision")
                    item.add_value("date", date_str)
                    yield item.load_item()

                elif any(url.endswith(x) for x in [".pdf", ".PDF", ".xlsx", "docx", ".exe", ".png", ".dav", ".mav"]):
                    continue
                else:
                    yield Request(
                        url=urllib.parse.urljoin(response.url, url),
                        headers={"Referer": response.url},
                        meta={"product": product},
                        callback=self.parse_url)
            
            '''
            elif any(href.endswith(x) for x in [".bin", ".elf", ".fdt", ".imx", ".chk", ".trx"]):
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%d-%b-%Y"])
                item.add_value("version", response.meta["version"])
                item.add_value("url", href)
                item.add_value("date", item.find_date(
                    link.xpath("following::text()").extract()))
                item.add_value("product", response.meta["product"])
                item.add_value("vendor", self.name)
                yield item.load_item()
            '''
