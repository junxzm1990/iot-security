from scrapy import Spider
from scrapy.http import Request, FormRequest, HtmlResponse

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error


class BelkinSpider(Spider):
    name = "belkin"
    allowed_domains = ["belkin.com", "belkin.force.com"]
    start_urls = ["https://www.belkin.com/us/search?text=firmware&type=support_downloads"]
    artical_base = "https://www.belkin.com/us/"
    def parse(self, response):
        for device in response.xpath("//ul[@class='support-list']//li/a/@href").extract():
            device_url = urllib.parse.urljoin(self.artical_base, device)

            yield Request(device_url,
                        callback=self.parse_product)
    
    def parse_product(self, response):
        product = response.xpath("//div[@class='article-header col-sm-8 col-lg-9']/h1/text()").extract()
        link = response.xpath("//a[@class='downLink']/@href").extract()
        if len(link) == 0:
            for firmware in response.xpath("//div[@class='article-accordian-content collapse-me']"):
                url = firmware.xpath(".//span[@style='font-family: arial,helvetica,sans-serif; font-size: 14px;']/a/@href").extract()
                if len(url) == 0:
                    url = firmware.xpath(".//span[@style='font-family: arial,helvetica,sans-serif;']/a/@href").extract()
                version = firmware.xpath("./@id").extract()
                for file_url in url:
                    if any(file_url.endswith(x) for x in [".bin", ".img", ".zip"]):
                        self.logger.debug("Mark")
                        self.logger.debug(file_url)
                        self.logger.debug(version)
                        self.logger.debug(product[0].split(" ")[0])
                        item = FirmwareLoader(item=FirmwareImage(),
                                          response=response)
                        item.add_value("version", version)
                        item.add_value("url", file_url)
                        item.add_value("product", product[0].split(" ")[0])
                        item.add_value("vendor", self.name)
                        yield item.load_item()
            
        else:
            for url in link:
                if any(url.endswith(x) for x in [".bin", ".img", ".zip"]):
                    item = FirmwareLoader(item=FirmwareImage(),
                            response=response)
                    item.add_value("url", url)
                    item.add_value("product", product)
                    item.add_value("vendor", self.name)
                    yield item.load_item()

