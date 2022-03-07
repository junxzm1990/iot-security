from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error

class TrendnetSpider(Spider):
    name = "trendnet"
    allowed_domains = ["trendnet.com"]
    start_urls = ["http://www.trendnet.com/support/"]

    def parse(self, response):
        for entry in response.xpath("//select[@id='subtype_id']/option"):
            if entry.xpath(".//text()"):
                text = entry.xpath(".//text()").extract()[0]
                href = entry.xpath("./@value").extract()[0]
                yield Request(
                    url=urllib.parse.urljoin(response.url, href),
                    meta={"product": text},
                    headers={"Referer": response.url},
                    callback=self.parse_product)
    def parse_product(self, response):
        product = response.xpath("//div[@class='col-lg-12 col-md-6 col-sm-6']/h2/text()").extract()[0].strip().split(" ")[0].strip()
        device_class = response.xpath("//div[@class='g-px-10--lg g-pt-10']/div/h1[@class='g-font-weight-300 mb-0']/text()").get().strip()
        for tab in response.xpath("//div[@class='row  g-pt-20 g-pb-10 g-px-15']"):
            text = tab.xpath("./div/div/a/text()").extract()
            href = tab.xpath("./div/div/a/@onclick").extract()
            version = tab.xpath("./div/p/text()").extract()
            date = tab.xpath("./div[2]/text()").extract()
            if len(text) == 0:
                continue
            if "firmware" in text[0].lower():
                if "open" in href[0]:
                    link = href[0].split('\'')[1]
                    url = urllib.parse.urljoin("https://www.trendnet.com", link)
                    url = url.replace("inc_downloading.asp?", "inc_downloading.asp?button=Continue+with+Download&Continue=yes&")
                self.logger.debug(date[1].strip())
                self.logger.debug(text[0])
                self.logger.debug(url)
                self.logger.debug(version)
                self.logger.debug(device_class)
                self.logger.debug(product)
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response, date_fmt=["%m/%d/%Y"])
                item.add_value("url", url)
                item.add_value("product", product)
                item.add_value("date", date[1].strip())
                if len(version) > 0:
                    item.add_value("version", version)
                item.add_value("vendor", self.name)
                yield item.load_item()
            

