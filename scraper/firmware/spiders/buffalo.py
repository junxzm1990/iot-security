from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

class BuffaloSpider(Spider):
    name = "buffalo"
    allowed_domains = ["buffalotech.com", "cdn.cloudfiles.mosso.com"]
    start_urls = ["https://www.buffalotech.com/products/category/wireless-networking"]

    def parse(self, response):
        for link in response.xpath('//article/div/a//@href').extract():
            product = link.split("/")[-1].split("-")
            name = product[1] + "-" + product[2] 
            yield Request(
                url=link,
                meta={"product":name},
                callback=self.parse_product)


    def parse_product(self, response):
        
        #<h3 class="firm">Firmware</h3>
        if response.xpath('//h3[@class="firm"]').extract():
            for tr in response.xpath('//*[@id="tab-downloads"]/table[1]/tbody/tr'):
                print(tr.extract())
                url = tr.xpath("./td[2]/a/@href").extract()[0]
                date = tr.xpath("./td[4]/text()").extract()[0]
                version = tr.xpath("./td[5]/text()").extract()[0]
                description = tr.xpath("./td[7]/text()").extract()[0]
                product = response.meta["product"]
                #self.logger.debug("Mark")
                #self.logger.debug(date)
                #self.logger.debug(product)
                #self.logger.debug(description)
                #self.logger.debug(url)
                item = FirmwareLoader(item=FirmwareImage(),
                                      response=response)
                                      
                item.add_value("version", version)
                item.add_value("description", description)
                item.add_value("url", url)
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                item.add_value("date", date)
                yield item.load_item()
