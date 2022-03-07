from scrapy import Spider
from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import urllib.request, urllib.parse, urllib.error
from scrapy.http import Request, HtmlResponse

class Tenvispider(Spider):
    name = "tenvis"
    allowed_domains = ["tenvis.com"]
    start_urls = ["http://apps.tenvis.com/Download/"]
    download = "http://apps.tenvis.com/Download/"

    def parse(self, response):
        release_date = response.xpath("//pre/text()").extract()
        #self.logger.debug(text)
        href = response.xpath("//pre/a/@href").extract()
        for i in range(len(href)):
            if not href[i].endswith("/"):
                if "firmware" in href[i].lower() and not href[i].endswith(".txt"):
                    self.logger.debug("File")
                    self.logger.debug(release_date[i-1].strip().split(" ")[0])
                    url = urllib.parse.urljoin(self.download, href[i])
                    product = href[i].split("/")[2]
                    if product == 'firmware':
                        product = href[i].split("/")[-1]
                    self.logger.debug(url)
                    self.logger.debug(product)
                    item = FirmwareLoader(item=FirmwareImage(), response=response)
                    item.add_value("url", url)
                    item.add_value("date", release_date[i-1].strip().split(" ")[0])
                    item.add_value("device_class", "IP Camera")
                    item.add_value("product", product)
                    item.add_value("vendor", self.name)
                    yield item.load_item()
            else:
                url = urllib.parse.urljoin(self.download, href[i])
                yield Request(url=url, callback=self.parse)
            '''
            idx = None
            for string in text:
                if "---" in string:
                    idx = int(string.split("-")[0])
                    break

            if not idx:
                continue

            '''
