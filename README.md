# Douban_scrapy
scrapy框架下爬取豆瓣电影的短评，电影按年份分好，每部电影一个文件夹（其包括h——好评,m——中评,l——差评）




1　 分别获取好，中，差的评论
2　 获取好，中，差的百分比
3　 获取名字，id，时间，评论内容和有用数

一部电影保存为一个文件夹，电影名字做文件夹名，里面按评论类型保存为csv文件
          
    movie_id　　user_name　　user_id　　comment　　type(H/M/L)　　time　　good　　source
