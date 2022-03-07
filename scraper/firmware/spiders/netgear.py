from scrapy import Spider
from scrapy.http import Request
import scrapy
from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error


class NetgearSpider(Spider):
    name = "netgear"
    allowed_domains = ["netgear.com"]
    # "http://downloadcenter.netgear.com/fr/", "http://downloadcenter.netgear.com/de/", "http://downloadcenter.netgear.com/it/", "http://downloadcenter.netgear.com/ru/", "http://downloadcenter.netgear.com/other/"]
    start_urls = ["http://www.netgear.com/support"]

    visited = []


    def parse(self, response):
        # choose the "Product Drilldown" button
        for link in response.xpath("//div[@class='product-category-product-intern']//div[contains(@id, 'product')]/@onclick"):
            link_url = link.get().split("=")[-1].replace("\'", "")
            product_url = urllib.parse.urljoin(response.url, link_url)
            yield Request(url=product_url,
                        callback=self.product_parse)
    def product_parse(self, response):
        #self.logger.debug(response.xpath("//section[@class='box articles']//div[@class='accordion-item']"))
        dsr = response.xpath('//div[@class="col frst"]/h1/text()').get()
        product = dsr.split(" ")[0]
        device_class = dsr.replace(product, "")
        #self.logger.debug(product)
        #self.logger.debug(dsr)
        #self.logger.debug(device_class)
        for firmware in response.xpath('//div[@class="accordion-item"]'):
            #self.logger.debug(firmware.xpath('./a[@class="accordion-title"]/@href').get())
            name = firmware.xpath('./a[@class="accordion-title"]/@href').get()
            version = name.split("Version")[-1]
            if "Firmware" in name:
                download = firmware.xpath('./div/div/a/@href').extract()[0]
                download_link = download.replace(" ", "%20")
                #self.logger.debug(download_link)
                if download.endswith(".exe") or download.endswith(".aspx"):
                    continue
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("version", version)
                #item.add_xpath("url", './div/div/a/@href')
                item.add_value("url", download_link)
                item.add_value("device_class", device_class)
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()


