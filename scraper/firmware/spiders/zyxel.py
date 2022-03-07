from scrapy import Spider
from scrapy.http import Request
from scrapy.http import FormRequest
from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import chompjs

import json
import urllib.request, urllib.parse, urllib.error

class ZyXELSpider(Spider):
    name = "zyxel"
    allowed_domains = ["zyxel.com"]
    start_urls = ["https://www.zyxel.com/us/en/products_services/home-home_routers.shtml?t=c",
                  "https://www.zyxel.com/us/en/products_services/home-personal_cloud_storage.shtml?t=c",
                  "https://www.zyxel.com/us/en/products_services/home-powerline_and_adapters.shtml?t=c"]

    #custom_settings = {"CONCURRENT_REQUESTS": 3}

    def parse(self, response):
        if "router" in response.url:
            device_class = "Router"
        elif "storage" in response.url:
            device_class = "Cloud Storage"
        elif "adapters" in response.url:
            device_class = "Adapter"
        product=response.xpath("//div[@class='section-filter-container small-grid']")
        for link in product.xpath("//div[@class='card']/a/@href").extract():
            url = link + "downloads"

            yield Request(
                    url=urllib.parse.urljoin(response.url, url), 
                    meta={"device_class":device_class},
                    callback=self.parse_product)
            #self.logger.debug(url)

        #self.logger.debug(script)
        #self.logger.debug(response.text)


    def parse_product(self, response):
    #    data = json.loads(response.text)
        table = response.xpath("//div[@class='col-md-11 col-md-offset-1']")
        for link in table.xpath("//a/@href").extract():
            if "firmware" in link.lower():
                self.logger.debug(link)
                yield FormRequest(
                    url=urllib.parse.urljoin(response.url, link), 
                    meta={"device_class":response.meta["device_class"]},
                    callback=self.parse_file)
    
    def parse_file(self, response):
        device_num = len(response.xpath("//td[@class='modelTd']//span").extract())
        link = response.xpath("//td[@class='downloadTd']//div/a/@data-filelink").extract()
        date = response.xpath("//td[@class='dateTd hidden-xs']//span/text()").extract()
        product = response.xpath("//td[@class='modelTd']//span/text()").extract()
        self.logger.debug(device_num)
        for i in range(device_num):
            #self.logger.debug("Mark")
            #self.logger.debug(product[i])
            #self.logger.debug(date[i])
            #self.logger.debug(link[2*i])
            item = FirmwareLoader(item=FirmwareImage(), response=response, date_fmt=["%m-%d-%Y"])
            item.add_value("date", date[i])
            item.add_value("url", link[2*i].replace(" ", "%20"))
            item.add_value("device_class", response.meta["device_class"])
            item.add_value("product", product[i])
            item.add_value("vendor", self.name)
            yield item.load_item()
