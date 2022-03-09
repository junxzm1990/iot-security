from scrapy import Spider
from scrapy.http import Request
from scrapy.http import FormRequest
from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import chompjs

import json
import urllib.request, urllib.parse, urllib.error

class RouterTechSpider(Spider):
    name = "router-tech"
    allowed_domains = ["routertech.org"]
    start_urls = ["https://www.routertech.org/ucp.php?mode=login"]
    url_base = "https://www.routertech.org"
    #custom_settings = {"CONCURRENT_REQUESTS": 3}
    def parse(self, response):
        sid = response.xpath("//input[@name='sid']/@value").get()
        self.logger.debug(sid)
        return FormRequest(
                    url=self.start_urls[0],
                    formdata={'username': '', 'password': '', 'redirect':'./ucp.php?mode=login', 'sid': sid, 'redirect':"index.php", "login":"Login"},
                    callback=self.after_login)


    def after_login(self, response):

        yield Request(
                url="https://www.routertech.org/viewforum.php?f=23",
                callback=self.parse_product)



    def parse_product(self, response):
        product=response.xpath("//div[@class='inner']/ul[@class='topiclist topics']")
        for release in product.xpath(".//li"):
            link = release.xpath(".//div[@class='list-inner']/a/@href").extract()[0]
            url=urllib.parse.urljoin(self.url_base, link) 
            
            yield Request(
                    url=urllib.parse.urljoin(self.url_base, link), 
                    callback=self.parse_file)
            
        
    
    def parse_file(self, response):
        title = response.xpath("//h2[@class='topic-title']/a/text()").extract()[0]
        version = title.split(" ")[2]
        date = title.split(" ")[-1].replace("(", "").replace(")", "")
        #self.logger.debug(title)
        #self.logger.debug(version)
        #self.logger.debug(date)
        attachbox = response.xpath("//dl[@class='attachbox']")
        for firmware in attachbox.xpath(".//dl[@class='file']"):
            link = firmware.xpath("./dt/a/@href").extract()[0]
            product = firmware.xpath("./dt/a/text()").extract()[0]
            if any(x in product for x in ["docs", "leds", "logs", "sources"]):
                continue
            url = urllib.parse.urljoin(self.url_base, link)
            #self.logger.debug(product)
            #self.logger.debug("Mark")
            item = FirmwareLoader(item=FirmwareImage(), response=response, date_fmt=["%m-%d-%Y"])
            item.add_value("date", date)
            item.add_value("url", url)
            item.add_value("device_class", "Router")
            item.add_value("product", product)
            item.add_value("vendor", self.name)
            item.add_value("version", version)
            yield item.load_item()
