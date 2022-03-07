from scrapy import Spider

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader

class SupermicroSpider(Spider):
    name = "supermicro"
    allowed_domains = ["supermicro.com"]
    start_urls = ["https://www.supermicro.com/support/resources/bios_ipmi.php?type=BMC"]

    def parse(self, response):
        for device in response.xpath("//tbody//tr"):
            product = device.xpath("./td[1]/a/text()").getall()
            link = device.xpath("./td[3]/a/@href").getall()[0]
            dsp = device.xpath("./td[6]/text()").getall()[0]
            download_url = link.replace("/about/policies/disclaimer.cfm?", "https://www.supermicro.com/support/resources/getfile.php?")
            if "Firmware" in dsp:
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("device_class", "BMC")
                item.add_value("url", download_url)
                item.add_value("product", product)
                item.add_value("vendor", self.name)
                yield item.load_item()
                #self.logger.debug(product)
                #self.logger.debug(download_url)
                #self.logger.debug(dsp)
