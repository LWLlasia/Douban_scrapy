# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy import log
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import os
import json
import csv
from douban_comment.items import DoubanCommentItem

class LessionSpider(scrapy.Spider):
    name = 'douban_comment'
    heasers = {
        'Host': 'movie.douban.com',
        'Referer': 'https://movie.douban.com/',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
    }

    def start_requests(self):

        yield scrapy.Request(url="https://accounts.douban.com/login?source=movie",callback=self.login,dont_filter=True,
                meta={'cookiejar':1 ,
                      'data': {
                      }
                    })
    def login(self,response):
        print 'Preparing login.....'
        sel = Selector(response)
        nodes = sel.xpath('//*[@class="captcha_image"]/@src').extract()
        if nodes:
            print nodes
            xerf = raw_input()
            return scrapy.FormRequest.from_response(
                    response,
                    formdata={
                        'capthcha-solution': xerf,
                        'phone': '18924891329',
                        'password': '85359529'


                    #     'form_email': '965202810@qq.com',
                    # 'form_password': 'gdufsiiip506'
                    },
                    callback=self.after_login, meta=response.meta
                )
        return scrapy.FormRequest.from_response(
                    response,
                    formdata={
                        'phone': '18924891329',
                        'password': '85359529'

                    # 'form_email': '965202810@qq.com',
                    # 'form_password': 'gdufsiiip506'
                    },
                    callback=self.after_login, meta=response.meta,
                )
    def after_login(self,response):
        if "authentication failed" in response.body:
            self.log("login failed", level=log.ERROR)
        clssifications = self.get_data_from_csvfile()
        for classification,year in clssifications.items():
            data = {}
            data.update(response.meta)
            data.update({'movie_name': classification,'movie_year':year})
            yield scrapy.Request(url='https://movie.douban.com/j/subject_suggest?q=' +classification ,callback=self.after_post,
                                 dont_filter=True, meta=data)

    def get_data_from_csvfile(self):
        classifications = {}
        for root, dirs, files in os.walk('/home/lasia/Desktop/豆瓣/'):
            # print root  # 当前目录路径
            # print dirs #当前路径下所有子目录
            # print files  #当前路径下所有非目录子文件
            for name in files:
                if 'csv' in name:
                    path = root + name
                    csv_reader = csv.DictReader(open(path))
                    for row in csv_reader:

                        classifications.update({row['movie_name']: row['movie_year']})

        return classifications

    def after_post(self,response):
        sites = json.loads(response.body_as_unicode())
        for i in sites:
            i = dict(i)
            if not i.has_key('year'):
                continue
            # if response.meta['year'] == ' ':
            #     yield scrapy.Request(url=i['url'].split("?")[0], callback=self.redirect, dont_filter=True,
            #                          meta=response.meta)
            #     return
            if i['year'] == response.meta['movie_year']:
                yield scrapy.Request(url=i['url'].split("?")[0], callback=self.redirect, dont_filter=True,
                                     meta=response.meta)
                return

    def redirect(self, response):
        data = {}
        data.update(response.meta)
        data.update({'id': response.url.split("/")[-2]})
        # yield scrapy.Request(url=response.url + "/comments?start=0&limit=20&sort=new_score&status=P&percent_type=",callback=self.get_comment_info, dont_filter=True, meta=data)
        yield scrapy.Request(url=response.url + "comments?start=0&limit=20&sort=new_score&status=P&percent_type=h",callback=self.get_comment_info, dont_filter=True, meta=data)
        yield scrapy.Request(url=response.url + "/comments?start=0&limit=20&sort=new_score&status=P&percent_type=m",callback=self.get_comment_info, dont_filter=True, meta=data)
        yield scrapy.Request(url=response.url + "/comments?start=0&limit=20&sort=new_score&status=P&percent_type=l",callback=self.get_comment_info, dont_filter=True, meta=data)
        # yield scrapy.Request(url=response.url + "/comments?status=F", callback=self.get_comment_info, dont_filter=True,meta=data)

    def get_comment_info(self,response):
        movie_data = DoubanCommentItem()
        comment_type = response.url.split('=')[-1]
        movie_data['movie_id'] = response.meta['id']


        comment_percent = response.xpath('*//div[@class="comment-filter"]/label/span[@class="comment-percent"]/text()')

        movie_name = response.meta['movie_name']
        movie_year = response.meta['movie_year']

        percent = []
        for i in comment_percent:
            # print str(i).split('data=u')[-1].replace('\'','').replace('>','')

            percent.append(str(i).split('data=u')[-1].replace('\'','').replace('>',''))
        if percent == []:
            percent = [0, 0, 0]
        # print percent
        # print "==========="



        if comment_type=='h':
            movie_data['type'] = comment_type + '_' + str(percent[0])
        if comment_type=='m':
            movie_data['type'] = comment_type + '_' + str(percent[1])
        if comment_type=='l':
            movie_data['type'] = comment_type + '_' + str(percent[2])
        for i in response.xpath('//div[@id="comments"]/div[@class="comment-item"]'):
            movie_data['user_name']= i.xpath('.//span[@class="comment-info"]/a/text()').extract_first()
            movie_data['user_id'] = i.xpath('.//a/@href').extract_first().split('people/')[-1].replace('/','')
            try:
                judge = self.judge_data(movie_data, response.meta)
                if judge:
                    continue
            except:
                pass



            movie_data['comment']= i.xpath('div[@class="comment"]/p/span[@class="short"]/text()').extract_first()
            movie_data['time'] = i.xpath('.//span[@class="comment-time "]/text()').extract_first().replace('\n                    ','')
            movie_data['good'] = i.xpath('.//span[@class="comment-vote"]/span/text()').extract_first()

            if i.xpath(".//span[contains(@class,'allstar')]/@class").extract_first() != None:
                rating = i.xpath(".//span[contains(@class,'allstar')]/@class").extract_first().replace("allstar", "").replace(
                " rating", "")
            else:
                rating = 'None'

            movie_data['source'] = rating
            print movie_name
            print movie_data
            # yield movie_data,movie_name

            self.save_data(movie_data,movie_name,movie_year)




        if response.xpath("//*[@class='next']/@href").extract_first() == None:
            print response.xpath("//*[@class='next']").extract_first()
            with open("/home/lasia/Desktop/豆瓣/had_checked.txt","a") as f:
                f.write(movie_name+'_'+movie_year+'\n')


            return
        else :
            url = response.url.split("?")[0]
            url += response.xpath("//*[@class='next']/@href").extract_first()
            yield scrapy.Request(url=url, callback=self.get_comment_info ,dont_filter = True,meta=response.meta)



    def save_data(self,data,movie_name,movie_year):

        headers = ["movie_id", "user_name", "user_id", "comment", "type", "time", "good", "source"]
        type = data['type'].split('_')[0]


        path = "/home/lasia/Desktop/douban/" +movie_year+'/'+ movie_name
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)

            with open("/home/lasia/Desktop/douban/" + movie_year+'/'+movie_name + '/h' + '.csv', 'a')as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            with open("/home/lasia/Desktop/douban/" + movie_year+'/'+movie_name + '/m' + '.csv', 'a')as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            with open("/home/lasia/Desktop/douban/" +movie_year+'/'+ movie_name + '/l' + '.csv', 'a')as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
        else:
            with open("/home/lasia/Desktop/douban/" +movie_year+'/'+ movie_name + '/'+type + '.csv', 'a')as csvfile:
                writer = csv.DictWriter(csvfile, headers)
                writer.writerow(data)

    def judge_data(self,data,start_data):
        judge = False
        type = data['type'].split('_')[0]
        root = "/home/lasia/Desktop/douban/" + start_data['movie_year']

        path = root + '/' +start_data['movie_name']+'/'+type + ".csv"
        # print path
        csv_reader = csv.DictReader(open(path))
        for row in csv_reader:
            # print row['user_id']
            if data['user_id'] == row['user_id']:
                judge = True
                continue

        return judge





















