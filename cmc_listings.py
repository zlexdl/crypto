import smtplib
import time
import json
import urllib.request

from util import send_pushplus
from email.mime.text import MIMEText
from email.header import Header
from config import global_config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class CmcCoinInfo(Base):
    __tablename__ = "cmc_coin_info"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    symbol = Column(String(50), nullable=True)
    name = Column(String(50), nullable=True)
    slug = Column(String(100), nullable=True)
    num_market_pairs = Column(Integer, nullable=True)
    date_added = Column(DateTime, nullable=True)
    max_supply = Column(Integer, nullable=True)
    circulating_supply = Column(Integer, nullable=True)
    total_supply = Column(Integer, nullable=True)
    platform_name = Column(String(100), nullable=True)
    platform_symbol = Column(String(50), nullable=True)
    token_address = Column(String(200), nullable=True)
    price_USD = Column(Float, nullable=True)
    volume_24h = Column(BigInteger, nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


def sendMail(mail_subject, mail_contents):
    # 发邮件 第三方 SMTP 服务
    mail_host = global_config.getRaw('mail', 'mail_host2')
    mail_user = global_config.getRaw('mail', 'mail_user2')
    mail_pass = global_config.getRaw('mail', 'mail_pass2')
    sender = global_config.getRaw('mail', 'sender2')
    receivers = ['6585852@qq.com']
    message = MIMEText(mail_contents, 'plain', 'utf-8')
    message['From'] = global_config.getRaw('mail', 'from2')
    message['Subject'] = Header(mail_subject, 'utf-8')
    message['To'] = "6585852@qq.com"
    print("邮件发送start")

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print("Error: " + str(e))
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


while True:
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=5&convert=USD&sort=date_added'

    print(datetime.now())
    try:

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'X-CMC_PRO_API_KEY': 'c83c47e9-677b-4770-9624-ffc0ea2d9942',
            'Accept': 'application/json'
        }

        opener = urllib.request.build_opener()
        # 发送request请求
        req = urllib.request.Request(url, headers=headers)
        res = opener.open(req)
        # 打印response code
        print(res.status)

        res_json = res.read().decode('utf8')
        # print(res_json)
        text = json.loads(res_json)
        datas = text['data']
        for data in datas:
            symbol = data['symbol']
            name = data['name']
            slug = data['slug']
            num_market_pairs = data['num_market_pairs']
            date_added = data['date_added']
            if data['max_supply'] is not None:
                max_supply = data['max_supply']
            else:
                max_supply = 0
            circulating_supply = data['circulating_supply']
            total_supply = data['total_supply']
            platform = data['platform']
            if platform:
                platform_name = platform['name']
                platform_symbol = platform['symbol']
                token_address = platform['token_address']
            else:
                platform_name = ''
                platform_symbol = ''
                token_address = ''
            quote = data['quote']
            if quote:
                price_USD = quote['USD']['price']
                volume_24h = quote['USD']['volume_24h']
            else:
                price_USD = 0
                volume_24h = 0

            if session.query(CmcCoinInfo).filter(CmcCoinInfo.symbol == symbol).count() == 0:
                added_date = datetime.strptime(date_added.replace('.000Z', ''), "%Y-%m-%dT%H:%M:%S")
                cmcCoinInfo = CmcCoinInfo(
                    symbol=symbol
                    , name=name
                    , slug=slug
                    , num_market_pairs=num_market_pairs
                    , date_added=added_date
                    , max_supply=max_supply
                    , circulating_supply=circulating_supply
                    , total_supply=total_supply
                    , platform_name=platform_name
                    , platform_symbol=platform_symbol
                    , token_address=token_address
                    , price_USD=price_USD
                    , volume_24h=volume_24h)
                print(symbol)
                session.add(cmcCoinInfo)
                session.commit()
                price = '{:.18f}'.format(price_USD)
                max_supply = str('{:,}'.format(max_supply))
                total_supply = str('{:,}'.format(total_supply))
                circulating_supply = str('{:,}'.format(circulating_supply))
                subject = 'New Coin: ' + symbol
                content = '<table><thead><tr><th></th><th></th></tr></thead><tbody><tr><td>name：</td><td>{}</td></tr><tr><td>symbol：</td><td>{}</td></tr><tr><td>最大供应量：</td><td>{}</td></tr><tr><td>总供应量：</td><td>{}</td></tr><tr><td>流通供应量：</td><td>{}</td></tr><tr><td>价格(U)：</td><td>{}</td></tr><tr><td>平台：</td><td>{}</td></tr><tr><td>加入时间：</td><td>{}</td></tr><tr><td>地址：</td><td></td></tr><tr><td colspan="2">{}</td></tr></tbody></table>'.format(
                    name, symbol, max_supply, total_supply, circulating_supply, price, platform_name, date_added, token_address)
                # sendMail(subject, content)
                send_pushplus(subject, content, '001')

    except Exception as e:
        session.rollback()
        print("Error: " + str(e))
        print("sleep 300s")
        time.sleep(300)
        continue
    print("sleep 300s")
    time.sleep(300)
print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
