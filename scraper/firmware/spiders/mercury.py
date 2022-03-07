#coding:utf-8

# spider update on 03/02/2021
from scrapy import Spider
from scrapy.http import Request

from firmware.items import FirmwareImage
from firmware.loader import FirmwareLoader
import urllib.request, urllib.parse, urllib.error

class MercurySpider(Spider):
    name = "mercury"
    vendor = "mercury"
    allowed_domains = ["mercurycom.com.cn"]
    start_urls = ["http://service.mercurycom.com.cn/download-list.html"]
    download_path = "http://service.mercurycom.com.cn"

    def parse(self, response):
        end_page = int(response.xpath("//*[@class='pagebar']//a[last()]//text()").extract()[0])
        cur_page = 0
        while cur_page < end_page:
            cur_page += 1
            url = 'http://service.mercurycom.com.cn/download-tip-software-{}-0-1.html'.format(cur_page)
            yield Request(
                url = url,
                headers={"Referer": response.url},
                callback = self.parse_list)

    def parse_list(self, response):
        href = response.xpath("//body//a/@href").extract()
        self.logger.debug("Mark")
        for link in href:
            if "download" in link:
                self.logger.debug(link)
                yield Request(
                    url = urllib.parse.urljoin(self.download_path, link),
                    headers={"Referer": response.url},
                    callback = self.parse_product
                    )

    def parse_product(self, response):
        link = response.xpath("//td[@class='col2']/a[@class='downloadBtn']/@href").extract()[0]
        #url = link.replace(" ", "%20")
        url_path = urllib.parse.urljoin(self.download_path, link).replace(" ", "%20")
        dsp = response.xpath("//tbody/tr/td[2]/p/text()").extract()[0]
        date = response.xpath("//tbody/tr[3]/td[2]/p/text()").extract()[0]
        product = dsp.split(" ")[0]
        version = dsp.split(" ")[-1]
        #self.logger.debug(type(url_path))
        #self.logger.debug(type(product))
        #self.logger.debug(type(date))
        #self.logger.debug(type(version))
        item = FirmwareLoader(item=FirmwareImage(), response=response)
        item.add_value("url", url_path)
        item.add_value("product", product)
        item.add_value("date", date)
        item.add_value("version", version)
        item.add_value("vendor", self.vendor)
        yield item.load_item()

