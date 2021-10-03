# This is a sample Python script.
import json
import urllib.request
import urllib.request
import requests
import os
from bs4 import BeautifulSoup


DOMAIN = 'https://www.block123.com/zh-hans'


def home(url):
    bs = get_html(url)

    tag_list_tail = bs.find_all(name='li', attrs={'class': "tag-list-tail"})
    for tail in tag_list_tail:
        sub_url = DOMAIN + tail.a['href']
        print(sub_url)

        sub_category = tail.a['title'].replace(' ', '').split('-')[0]
        category = tail.a['title'].replace(' ', '').split('-')[1]
        print(sub_category)
        print(category)
        pages(sub_url, category, sub_category)


def get_html(url):
    req = set_header(url)
    with urllib.request.urlopen(req) as response:
        html = (response.read())
    bs = BeautifulSoup(html, "html.parser")
    return bs


def pages(url, category, sub_category):
    bs = get_html(url)

    last_li = bs.find(name='li', attrs={'class': "last page-item"})
    max_page = int(last_li.previous_element)
    for num in range(1, int(max_page)):
        sub_url = url + '&page=' + str(num)
        print(sub_url)
        page(sub_url, category, sub_category)

def parse_json(s):
    begin = s.find('{')
    end = s.rfind('}') + 1
    return json.loads(s[begin:end])

def page(url, category, sub_category):
    bs = get_html(url)

    # lis = bs.find_all(name='li', attrs={'class': "nav-item"})

    lis = parse_json(str(bs.find_all(name='script', attrs={'id': "__NEXT_DATA__"})[0]))
    for result in lis['props']['pageProps']['data']['results']:
        sub_url = DOMAIN + result['get_absolute_url']
        print(sub_url)
        item(sub_url, category, sub_category)


def item(social_url, category, sub_category):
    sub_url = DOMAIN + social_url
    print(sub_url)
    bs = get_html(sub_url)
    json = parse_json(str(bs.find_all(name='script', attrs={'id': "__NEXT_DATA__"})[0]))
    data = json['props']['pageProps']['data']
    name = data['name']
    bio = data['bio']
    description = data['description']
    logo_url = data['logo_url']
    save_name = download_img(logo_url, name)
    web_site = data['web_site']
    symbol = data['symbol']
    social = data['social']
    twitter = social.get('twitter', '')
    facebook = social.get('facebook', '')
    medium = social.get('medium', '')
    blog = social.get('blog', '')
    telegram = social.get('telegram', '')
    github = social.get('github', '')
    discord = social.get('discord', '')
    members = data['members']
    for member in members:
        name = member['name']
        bio = member['bio']
        logo_url = member['logo_url']
        web_site = member['web_site']
        save_name = download_img(logo_url, name)


    experiences = data['experiences']
    print("experiences=" + experiences)
    portfolios = data['portfolio']
    for portfolio in portfolios:
        name = portfolio['name']
        bio = portfolio['bio']
        logo_url = portfolio['logo_url']
        web_site = portfolio['web_site']
        save_name = download_img(logo_url, name)

    portfolios = data['portfolio']
    for investor in portfolios:
        name = investor['name']
        bio = investor['bio']
        logo_url = investor['logo_url']
        web_site = investor['web_site']
        save_name = download_img(logo_url, name)

    features = data['features']
    print("features=" + features)
    related = data['related']
    print("related=" + related)




def getInfo(title):
    bs = title.find_next_sibling()
    for item in bs.contents:
        if item != '\n':
            tds_soup = BeautifulSoup(str(item), "html.parser")
            image = tds_soup.find(name='img', attrs={'class': "lazy"})['data-original'].split('?')[0]
            name = tds_soup.find(name='div', attrs={'class': "name"}).string.replace('\n', '').replace(' ', '_')
            introduction = tds_soup.find(name='div', attrs={'class': "bottom-block"}).string.replace('\n', '')
            print(image)
            print(name)
            print(introduction)
            download_img(image, name)




def create_folder(file_name):
    path = os.path.split(file_name)[0]
    if path != '' and not os.path.exists(path):
        os.makedirs(path)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def getInfo(title):
    bs = title.find_next_sibling()
    for item in bs.contents:
        if item != '\n':
            tds_soup = BeautifulSoup(str(item), "html.parser")
            image = tds_soup.find(name='img', attrs={'class': "lazy"})['data-original'].split('?')[0]
            name = tds_soup.find(name='div', attrs={'class': "name"}).string.replace('\n', '').replace(' ', '_')
            introduction = tds_soup.find(name='div', attrs={'class': "bottom-block"}).string.replace('\n', '')
            print(image)
            print(name)
            print(introduction)
            download_img(image, name)


def download_img(img_url, name):
    img_url = img_url.split('?')[0]
    name = name.replace(' ', '_')
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
    req.add_header('user-agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/92.0.4515.159 Safari/537.36')
    return req


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    url = 'https://www.block123.com/zh-hans/'
    home(url)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
