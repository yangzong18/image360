# -*- coding: utf-8 -*-
import pymysql
import logging
from twisted.enterprise import adbapi

class MysqlPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
 
    @classmethod
    def from_settings(cls,settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        # """
        # 数据库建立连接
        # :param settings: 配置参数
        # :return: 实例化参数
        # """
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            use_unicode=True,
            cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
        )
        # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
        dbpool = adbapi.ConnectionPool('pymysql',**adbparams)
        # 返回实例化参数
        return cls(dbpool)
 
 
    def process_item(self,item,spider):
        # """
        # 使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
        # """
        query = self.dbpool.runInteraction(self.do_insert,item)  # 指定操作方法和操作数据
        # 添加异常处理
        query.addCallback(self.handle_error)  # 处理异常

        return item
 

    def do_insert(self,cursor,item):
        # 对数据库进行插入操作，并不需要commit，twisted会自动commit
        insert_sql = """insert into image_360(url,title,thumb) VALUES(%s,%s,%s)"""
        cursor.execute(insert_sql,(item['url'],item['title'],item['thumb']))
 
    def handle_error(self,failure):
        if failure:
            # 打印错误信息
            logging.error(failure)


from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield Request(item['url'])

    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Download Failed')
        return item
