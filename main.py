# This is a sample Python script.
import json
import urllib.request
import urllib.request
import requests
import os
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta
import time
from util import parse_json, get_session, get_random_useragent, get_random_useragent
from config import global_config
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='logs/block123.log', level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')
DOMAIN = 'https://www.block123.com'
engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Investment(Base):
    __tablename__ = "investment"  # 数据库中保存的表名字
    name = Column(String(50), index=True, primary_key=True)
    cate = Column(String(50), nullable=True)
    cate_name = Column(String(50), nullable=True)
    bio = Column(String(50), nullable=True)
    description = Column(String(50), nullable=True)
    logo_url = Column(String(50), nullable=True)
    save_name = Column(String(50), nullable=True)
    web_site = Column(String(50), nullable=True)
    symbol = Column(String(50), nullable=True)
    twitter = Column(String(50), nullable=True)
    facebook = Column(String(50), nullable=True)
    medium = Column(String(50), nullable=True)
    blog = Column(String(50), nullable=True)
    telegram = Column(String(50), nullable=True)
    github = Column(String(50), nullable=True)
    discord = Column(String(50), nullable=True)
    reference_name = Column(String(50), nullable=True)
    relationship = Column(String(20), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


def home(url):
    bs = get_html(url)

    tag_list_tail = bs.find_all(name='div', attrs={'class': "snippets-wrapper"})
    for tail in tag_list_tail:
        sub_url = DOMAIN + tail.a['href']
        if sub_url == 'https://www.block123.com/zh-hans/c/184982400121.htm':
            continue
        if sub_url == 'https://www.block123.com/zh-hans/c/400455894778.htm':
            continue
        if sub_url == 'https://www.block123.com/zh-hans/c/852112675460.htm':
            continue
        # if sub_url == 'https://www.block123.com/zh-hans/c/182175709311.htm':
        #     continue
        print(sub_url)
        logging.info('home+' + sub_url)
        pages(sub_url)

    # tag_list_tail = bs.find_all(name='li', attrs={'class': "tag-list-tail"})
    # for tail in tag_list_tail:
    #     sub_url = DOMAIN + tail.a['href']
    #     print(sub_url)
    #
    #     sub_category = tail.a['title'].replace(' ', '').split('-')[0]
    #     category = tail.a['title'].replace(' ', '').split('-')[1]
    #     print(sub_category)
    #     print(category)
    #     pages(sub_url, category, sub_category)


def get_html(url):
    is_error = 1
    while is_error == 1:
        try:

            req = set_header(url)
            with urllib.request.urlopen(req) as response:
                html = (response.read())
            bs = BeautifulSoup(html, "html.parser")
            is_error = 0
        except Exception as err:
            print(err)
            print('sleep 10s')
            time.sleep(10)
            is_error = 1
    return bs


def pages(url):
    bs = get_html(url)

    last_li = bs.find(name='li', attrs={'class': "last page-item"})
    max_page = int(last_li.previous_element)
    for num in range(1, int(max_page)):
        if url.find('https://www.block123.com/zh-hans/c/184982400121.htm?tid=66') >= 0 and num < 41:
            continue
        sub_url = url + '&page=' + str(num)
        print('pages=' + sub_url)
        logging.info('pages=' + sub_url)
        page(sub_url)


def parse_json(s):
    begin = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[begin:end])


def page(url):
    bs = get_html(url)

    # lis = bs.find_all(name='li', attrs={'class': "nav-item"})

    lis = parse_json(str(bs.find_all(name='script', attrs={'id': "__NEXT_DATA__"})[0]))
    for result in lis['props']['pageProps']['data']['results']:
        sub_url = DOMAIN + '/zh-hans' + result['get_absolute_url']
        print(sub_url)
        logging.info('page=' + sub_url)
        item(sub_url, '', '')


def item(sub_url, reference_name, relationship):
    bs = get_html(sub_url)
    _json = parse_json(str(bs.find_all(name='script', attrs={'id': "__NEXT_DATA__"})[0]))
    data = _json['props']['pageProps']['data']
    save(data, reference_name, relationship)

    if relationship != '':
        return
    reference_name = data['name'].replace(' ', '_')
    members = data['members']
    # for member in members:
    #     sub_item(member, reference_name, 'member')

    portfolios = data['portfolio']
    print("portfolios=" + str(portfolios))
    for portfolio in portfolios:
        sub_item(portfolio, reference_name, 'portfolio')

    experiences = data['experiences']
    print("experiences=" + str(experiences))
    for experience in experiences:
        sub_item(experience, reference_name, 'experience')
    investors = data['investors']
    print("investors=" + str(investors))
    for investor in investors:
        sub_item(investor, reference_name, 'investor')

    # features = data['features']
    # print("features=" + str(features))
    # for feature in features:
    #     sub_item(feature, reference_name, 'feature')
    # relateds = data['related']
    # print("related=" + str(relateds))
    # for related in relateds:
    #     sub_item(related, reference_name, 'related')


def sub_item(investor, reference_name, relationship):
    get_absolute_url = investor['get_absolute_url']
    if get_absolute_url.find('zh-hans') > 0:
        sub_url = DOMAIN + get_absolute_url
    else:
        sub_url = DOMAIN + '/zh-hans' + get_absolute_url
    print(sub_url)
    logging.info('sub_item=' + sub_url)
    item(sub_url, reference_name, relationship)


def save(data, reference_name, relationship):
    _name = data['name'].replace(' ', '_')
    print('name=' + _name)
    logging.info('save=' + _name)
    if session.query(Investment).filter(Investment.name == _name,
                                        Investment.reference_name == reference_name).count() > 0:
        return

    try:
        social = data['social']
        if data.get('symbol') is None:
            _save_name = _name
        else:
            _save_name = data.get('symbol')
        investment = Investment(
            name=_name
            , cate=data['cate']['cname']
            , cate_name=data['cate']['ename']
            , bio=data['bio']
            , description=data['description'][0:999]
            , logo_url=data['logo_url']
            , save_name=download_img(data['logo_url'], _save_name)
            , web_site=data['web_site']
            , symbol=data['symbol']
            , twitter=social.get('twitter', '')
            , facebook=social.get('facebook', '')
            , medium=social.get('medium', '')
            , blog=social.get('blog', '')
            , telegram=social.get('telegram', '')
            , github=social.get('github', '')
            , discord=social.get('discord', '')
            , reference_name=reference_name
            , relationship=relationship
        )

        session.add(investment)
        session.commit()
        time.sleep(2)

    except Exception as err:
        session.rollback()
        print('reference_name=' + reference_name)
        print(err)
        time.sleep(60)
        save(data, reference_name, relationship)


def create_folder(file_name):
    path = os.path.split(file_name)[0]
    if path != '' and not os.path.exists(path):
        os.makedirs(path)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def download_img(img_url, name):
    img_url = img_url.split('?')[0]
    # 后缀名
    save_name_suffix = img_url[-3:]
    # 保存的名字
    save_name = 'ptotos/' + name + '.{}'.format(save_name_suffix)
    ret = requests.get(img_url)
    # 图片信息
    info = ret.content
    # 不存在文件就创建
    create_folder(save_name)
    # 二进制方式写入
    with open(save_name, 'wb') as f:
        f.write(info)

    return save_name


def create_folder(file_name):
    path = os.path.split(file_name)[0]
    if path != '' and not os.path.exists(path):
        os.makedirs(path)


def set_header(url):
    req = urllib.request.Request(url)
    req.add_header('accept',
                   'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                   'application/signed-exchange;v=b3;q=0.9')
    # req.add_header('accept-encoding', 'gzip, deflate, br')
    req.add_header('accept-language', 'zh-CN,zh;q=0.9,ja;q=0.8,zh-TW;q=0.7')
    req.add_header('cache-control', 'max-age=0')
    req.add_header('cookie',
                   '_ga=GA1.2.95021594.1631015178; _gid=GA1.2.390103052.1631015178; '
                   'Hm_lvt_4f7c3b36ed0491f90852e05efd64e62f=1631015178; '
                   'messages="d052e50f63db745b560d2085b6383570aef0f696$[[\"__json_message\"\0540\05425\054\"\\u4ee5 '
                   'xxxxx@163.com..\\u8eab\\u4efd\\u6210\\u529f\\u767b\\u5f55\"]]"; '
                   'csrftoken=xqdDCkVmi36rtWGGYnpPnnSwDJdqdfD5GxDaiteeea6NBiaybdIdZ8JTFNMZul42; '
                   'sessionid=3amg0vba3m5bi15sb1yvefx0oiecqyj0; Hm_lpvt_4f7c3b36ed0491f90852e05efd64e62f=1631018691')
    req.add_header('referer', 'https://www.block123.com/zh-hans/')
    req.add_header('sec-ch-ua', '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"')
    req.add_header('sec-ch-ua-mobile', '?0')
    req.add_header('sec-fetch-dest', 'document')
    req.add_header('sec-fetch-mode', 'navigate')
    req.add_header('sec-fetch-site', 'same-origin')
    req.add_header('sec-fetch-user', '?1')
    req.add_header('upgrade-insecure-requests', '1')
    req.add_header('user-agent', get_random_useragent())
    return req


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    url = 'https://www.block123.com/zh-hans/'
    home(url)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
