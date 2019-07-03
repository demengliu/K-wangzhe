import json
import re
import os
import requests
from lxml import etree

"""
原创爬虫

爬取以下内容

保存英雄皮肤大图片 


分析页面　这一步最重要
1首先分析页面,发现页面response里面的数据和element页面的数据不一样，响应的数据是动态渲染的
2那我们不能直接提取详细英雄的url，然后找找有没有json数据的url　http://pvp.qq.com/web201605/js/herolist.json
3找到一个json数据的url,点开发现有英雄id相关的信息,　可以用英雄id构造英雄详细页面
4提取英雄详细页面的相关信息,大部分信息都可以直接xpath提取，少部分信息在json数据里面,比如铭文,所有装备等等
这三个json数据里面包含有所有的相关信息，可以从页面提取的id然后从里面找到对应的详细信息
        http://pvp.qq.com/web201605/js/item.json
        http://pvp.qq.com/web201605/js/summoner.json
        http://pvp.qq.com/web201605/js/ming.json

"""


class KingWangZhe(object):
    """
    爬取王者荣耀英雄相关信息
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        }

        self.temp_url = 'http://pvp.qq.com/web201605/herodetail/{}.shtml'

        self.json_url = 'http://pvp.qq.com/web201605/js/herolist.json'

        self.temp_img_url = 'https://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{}/{}-bigskin-{}.jpg'

    def prase_hreo_list_json(self):
        """
        获取英雄信息的json数据
        :return:
        """
        response = requests.get(self.json_url, headers=self.headers)
        json_data = json.loads(response.text)
        return json_data

    def get_url_list(self, json_data):
        """
        构建英雄详细页的url
        :param id:
        :return:
        """
        url_list = []
        for item in json_data:
            url = self.temp_url.format(item['ename'])
            url_list.append(url)

        return url_list

    def prase_details(self, url):
        """
        解析详细页面的url
        :param url:
        :return:
        """
        response = requests.get(url, headers=self.headers)
        html_str = response.content.decode('GBK')
        return html_str

    def get_content(self, html_str, url):
        """
        xpath提取页面数据
        英雄相关信息全在这个页面，自己用xpath提取
        然后装备，技能等信息只找到id号或者名称
        这三个json数据里面包含有所有的相关信息，可以从页面提取的id然后从里面找到对应的详细信息
        http://pvp.qq.com/web201605/js/item.json
        http://pvp.qq.com/web201605/js/summoner.json
        http://pvp.qq.com/web201605/js/ming.json
        :param html_str:
        :return:
        """
        r = etree.HTML(html_str)
        content = {}
        try:
            # img_url = r.xpath("//div[@class='zk-con1 zk-con']/@style")[0]  # 提取大图片的url
            # img_url = re.findall(r'(\/\/game.*\.jpg)', img_url)[0]

            hero_name = r.xpath("//h2[@class='cover-name']/text()")[0]
            hero_id = int(re.findall(r"\/(\d+)\.shtml", url)[0])
            img_list = r.xpath("//ul[@class='pic-pf-list pic-pf-list3']/@data-imgname")[0]
            img_list = img_list.split("|")
            # content['img_url'] = "https:" + img_url
            content['hero_name'] = hero_name
            content['hero_id'] = hero_id
            content['detail_url'] = url
            content['img_list'] = img_list
            # 暂时我只提取了背景大图的url和英雄name
            return content
        except Exception as e:
            print("图片提取失败", e)
            return None

    def save_img(self, content):

        try:
            if not os.path.exists("./imgs2"):
                # 判断是否创建文件夹
                os.mkdir("./imgs2")
            for item in content['img_list']:
                img_url = self.temp_img_url.format(content['hero_id'], content['hero_id'],
                                                   content['img_list'].index(item) + 1)
                response = requests.get(img_url, headers=self.headers)
                with open("./imgs2/" + content['hero_name'] + item + '.jpg', 'wb') as f:
                    f.write(response.content)
                print(content['hero_name']+item, "大图保存成功")
        except Exception as e:
            print("图片保存失败", e)

    def run(self):
        """"""
        # html_str = self.prase_url(self.start_url)
        json_data = self.prase_hreo_list_json()  # 提取json数据
        url_list = self.get_url_list(json_data)  # 获取详细页面的url列表
        for url in url_list:
            html_str = self.prase_details(url)  # 解析详细页面的url
            content = self.get_content(html_str, url)  # 解析详
            print(content)
            self.save_img(content)


if __name__ == '__main__':
    rongyao = KingWangZhe()
    rongyao.run()
