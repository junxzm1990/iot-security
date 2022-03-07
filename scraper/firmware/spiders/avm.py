
from calendar import month_abbr
from re import search
from typing import Generator, Union

from scrapy import Request, Spider
from scrapy.http import Response
from firmware.loader import FirmwareLoader
from firmware.items import FirmwareImage

import json



class AvmSpider(Spider):
    handle_httpstatus_list = [404]
    name = 'avm'
    allowed_domains = ['download.avm.de']
    start_urls = ['http://download.avm.de/fritzbox/',
                    'http://download.avm.de/fritzwlan/',
                    'http://download.avm.de/fritzpowerline/']
    def parse(self, response: Response) -> Generator[Request, None, None]:
        for product_url in self.extract_links(response=response, ignore=('beta', 'tools', 'license', '..')):
            yield Request(url=product_url, callback=self.parse_product)

    def parse_product(self, response: Response) -> Union[Generator[FirmwareImage, None, None], Generator[Request, None, None]]:
        path = response.request.url.split('/')[:-1]
        if path[-1] == 'fritz.os':
            yield from self.parse_firmware(response=response, device_name=path[-3])
        else:
            for sub_directory in self.extract_links(response=response, ignore=('recover', '..')):
                yield Request(url=response.urljoin(sub_directory), callback=self.parse_product)

    def parse_firmware(self, response: Response, device_name: str) -> Generator[FirmwareImage, None, None]:
        release_dates = self.extract_dates(response)
        for index, file_url in enumerate(self.extract_links(response=response, ignore='..')):
            if file_url.endswith('.image'):
                yield from self.prepare_item_pipeline(meta_data=self.prepare_meta_data(device_name=device_name, release_date=release_dates[index], file_url=file_url))
    @staticmethod
    def prepare_item_pipeline(meta_data: dict) -> Generator[FirmwareImage, None, None]:
        loader = FirmwareLoader(item=FirmwareImage(), selector=meta_data['file_urls'])
        loader.add_value('url', meta_data['file_urls'])
        loader.add_value('vendor', meta_data['vendor'])
        loader.add_value('product', meta_data['device_name'])
        loader.add_value('device_class', meta_data['device_class'])
        loader.add_value('version', meta_data['firmware_version'])
        loader.add_value('date', meta_data['release_date'])
        yield loader.load_item()

    def prepare_meta_data(self, device_name: str, release_date: str, file_url: str) -> dict:
        return {
            'file_urls': [file_url],
            'vendor': 'AVM',
            'device_name': device_name,
            'firmware_version': self.extract_version(firmware=file_url.split('/')[-1], product_specifier=device_name),
            'device_class': self.map_device_class(product=device_name),
            'release_date': release_date
        }


        
    @staticmethod
        
    def map_device_class(product: str) -> str:
        if product.startswith(('fritzrepeater', 'fritzwlan-repeater')):
            return 'Repeater'
        if product.startswith('fritzwlan-usb'):
            return 'Wifi-Stick'
        if product.startswith('fritzpowerline'):
            return 'PLC Adapter'
        return 'Router'
    @staticmethod
    def extract_links(response: Response, ignore: Union[str, tuple]) -> list:
        return [response.urljoin(p) for p in response.xpath('//a/@href').extract() if not p.startswith(ignore)]


    def extract_dates(self, response: Response) -> list:
        release_dates = list()
        for text in response.xpath('//pre/text()').extract():
            match = search(r'(\d{2}-\w{3}-\d{4})', text)
            if match:
                release_dates.append(self.convert_date(match.group(1)))
        return release_dates
    @staticmethod
    def convert_date(date: str) -> str:
        day_month_year = date.split('-')
        month_digit = list(month_abbr).index(day_month_year[1])
        day_month_year[1] = str(month_digit) if month_digit > 9 else '0' + str(month_digit)
        return '-'.join(day_month_year)

    def extract_version(self, firmware: str, product_specifier: str) -> str:
        try:
            if 'fritz.powerline' in firmware:
                return self.extract_powerline_version(firmware, product_specifier)
            return search(r'FRITZ\.(Box|Powerline|Repeater)_(\w+)(\.(\w{2}-)+\w{2}\.)?([-\.])?(.*)\.image', firmware).group(6)
        except (AttributeError, IndexError, ValueError):
            return '0.0'

    def extract_powerline_version(self, firmware, product_specifier):
        for hardware_number in self.generate_permutations(array=product_specifier.split('-')[1:], prefix='', index=0):
            matches = search(r'(?:' + r''.join(hardware_number.upper()) + r')_(.*).image', firmware)
            if matches:
                return matches.group(1).replace('_', '.')
            raise ValueError('No version found in firmware string')

    def generate_permutations(self, array: list, prefix: str, index: int) -> Generator[str, None, None]:
        if index < len(array) - 1:
            for result in self.generate_permutations(array=array, prefix=prefix + array[index] + '_', index=index + 1):
                yield result
                for result in self.generate_permutations(array=array, prefix=prefix + array[index], index=index + 1):
                    yield result
                else:
                    yield prefix + array[index]


