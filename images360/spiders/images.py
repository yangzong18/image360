# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, Spider
from urllib.parse import urlencode
import json
from images360.items import ImageItem

class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['images.so.com']
    start_urls = ['http://images.so.com/']

    def start_requests(self):
        data = {'ch':'photography', 'listtype':'new'}
        # http://images.so.com/zj?ch=photography&sn=30&listtype=new&temp=1
        base_url = 'http://images.so.com/zj?'
        for page in range(1, self.settings.get('MAX_PAGE')+1):
            data['sn'] = 30 * page
            params = urlencode(data)
            url = base_url+params
            yield Request(url, self.parse)

    def parse(self, response):
        # self.logger.debug(response.text)
        result = json.loads(response.text)

        for image in result.get('list'):
            item = ImageItem()
            item['id'] = image.get('imageid')
            item['url'] = image.get('qhimg_url')
            item['title'] = image.get('group_title')
            item['thumb'] = image.get('qhimg_thumb_url')
            yield item
