from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error

class UbloxSpider(Spider):
    name = "ublox"
    allowed_domains = ["u-blox.com"]
    start_urls = ["https://www.u-blox.com/en/product-resources/field_file_category/firmware-update-223"]

    def parse(self, response):
        for firmware in response.xpath("//div[@class='file-entity-teaser__col-left']"):
            product = firmware.xpath("./div[@class='file-entity-teaser__title']/h2/a/text()").extract()
            url = firmware.xpath("./div[@class='file-entity-teaser__title']/h2/a/@href").extract()
            date = firmware.xpath("./div[@class='file-entity-teaser__date']/p/text()").extract()
            item = FirmwareLoader(
                        item=FirmwareImage(), response=response)
            self.logger.debug(url[0])
            self.logger.debug(product[0])
            item.add_value("url", url)
            item.add_value("product", product[0])
            if len(date) > 0:
                item.add_value("date", date[0].strip())
                self.logger.debug(date[0].strip())
            item.add_value("vendor", self.name)
            yield item.load_item()


    def parse_product(self, title):
        import re
        p = " for ([a-zA-Z0-9\-_]+)$"
        ret = re.findall(p, title)
        if ret:
            product = ret[0]
        else:
            product = title.replace('u-blox', '').strip().split(' ')[0]
        return product
