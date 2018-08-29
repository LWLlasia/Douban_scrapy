# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

from selenium import webdriver
from scrapy.http import HtmlResponse
import time
from time import sleep
from selenium.common.exceptions import NoSuchElementException
class PhantomJSMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):

        if request.meta.has_key('search'):
            # print request.headers.getlist('Cookie')
            print request.meta['name'] +"???????"+request.meta['year']
            try:
                driver = webdriver.PhantomJS()
                driver.get(request.url)
                # if len(driver.find_elements_by_xpath("//input[@id='inp-query']"))==0:

                driver.find_element_by_xpath("//input[@id='inp-query']").send_keys(request.meta['name'])
                driver.find_element_by_xpath("//input[@type='submit']").click()
                content = driver.page_source.encode('utf-8')
                content = driver.page_source.encode('utf-8')
                year = request.meta['year']
                for i in driver.find_elements_by_xpath("//div[contains(@class,'sc-bZQynM')]") :
                    print i
                    movie_year = i.find_element_by_xpath(".//div//div//div//a[@class='title-text']").text
                    movie_year = movie_year.split("(")[1].replace(")","")
                    if movie_year != year:
                        print movie_year,year
                        continue
                    url = driver.find_element_by_xpath("//div[contains(@class,'sc-bZQynM')]//div//a").get_attribute("href")
                    print url
                    driver.quit()
                    return HtmlResponse(url=url, encoding='utf-8', body=content, request=request)
            except NoSuchElementException as e:
                print e.message,"retrying"
                driver = webdriver.PhantomJS()
                driver.get(request.url)
                driver.find_element_by_xpath('//a').click()


    def process_exception(self, request, exception, spider):
        # if exception=='NoSuchElementException' :
        print 'wrong: '+exception
        return request

class DoubanCommentSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
