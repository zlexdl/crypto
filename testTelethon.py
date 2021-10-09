from telethon import TelegramClient, events, sync
import socks
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from elasticsearch import Elasticsearch
import logging
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from telethon.tl.types import PeerChat, PeerChannel

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
NOW = datetime.now()
logging.basicConfig(filename='logs/telethon.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT,
                    encoding='utf-8')

# api_id = 5433729
# api_hash = '0e89dcb2d76fad7f5d7cd55c3a953cf0'
# phone_number = '+8615566817746'

api_id = 7928011
api_hash = 'b74852d9349c2b9b5f5a287ef1120733'
phone_number = '+8618242025966'

engine = create_engine("mysql+pymysql://root:password@192.168.1.32:3306/hwdb?charset=utf8")
Base = declarative_base()


class Monitor(Base):
    __tablename__ = "monitor"  # 数据库中保存的表名字

    id = Column(Integer, primary_key=True)
    asset_pair = Column(String(20), nullable=False)
    asset = Column(String(10), index=True, nullable=False)
    asset_base = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    price_incr = Column(Float, nullable=False)
    volume_incr = Column(BigInteger, nullable=False)
    ex = Column(String(10), nullable=False)
    updated_at = Column(DateTime, default=NOW)


def sendMail(mail_subject, mail_contents):
    # 发邮件 第三方 SMTP 服务
    mail_host = "smtp.126.com"  # 设置服务器
    mail_user = "bsv_whale_alert"  # 用户名
    mail_pass = "FFUNDLIEMVWJDCNV"  # 口令
    sender = 'bsv_whale_alert@126.com'

    # mail_host="smtp.sohu.com"  #设置服务器
    # mail_user="zhanglei_2017"    #用户名
    # mail_pass="WMJ2HF40ZL76Q"   #口令    
    # sender = 'zhanglei_2017@sohu.com'
    # dlwg10g@dingtalk.com 梨
    # btcbch2017@dingtalk.com bsv666
    # d875x9g@dingtalk.com 于
    # sangxiaomeng@dingtalk.com C 哥
    # txy-87evmhmuw@dingtalk.com hanno

    receivers = ['frm5966@dingtalk.com', 'txy-87evmhmuw@dingtalk.com', 'sangxiaomeng@dingtalk.com',
                 'd875x9g@dingtalk.com', 'btcbch2017@dingtalk.com', 'dlwg10g@dingtalk.com']
    # receivers = ['frm5966@dingtalk.com','sangxiaomeng@dingtalk.com', 'rvs-6955bte6b@dingtalk.com',
    # 'd875x9g@dingtalk.com','54644902@qq.com','btcbch2017@dingtalk.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText(mail_contents, 'plain', 'utf-8')
    message['From'] = "bsv_whale_alert<bsv_whale_alert@126.com>"
    # message['From'] = "zhanglei_2017<zhanglei_2017@sohu.com>" message['To'] =  "frm5966@dingtalk.com,
    # sangxiaomeng@dingtalk.com, rvs-6955bte6b@dingtalk.com,d875x9g@dingtalk.com,54644902@qq.com,
    # btcbch2017@dingtalk.com"
    message[
        'To'] = "frm5966@dingtalk.com,txy-87evmhmuw@dingtalk.com,sangxiaomeng@dingtalk.com, d875x9g@dingtalk.com," \
                "btcbch2017@dingtalk.com, dlwg10g@dingtalk.com "

    subject = mail_subject
    message['Subject'] = Header(subject, 'utf-8')
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


# client = TelegramClient(phone_number, api_id, api_hash, proxy=("HTTP", 'localhost', 10809))
client = TelegramClient(phone_number, api_id, api_hash)
print("1")
client.start()
print("2")
print(client.get_me())

Session = sessionmaker(bind=engine)

session = Session()

@client.on(events.NewMessage(chats=[PeerChannel(-1001329310076)]))
# @client.on(events.NewMessage(chats='cointrendz_pumpdetector'))
# @client.on(events.NewMessage(chats='test_zlexdl'))
async def my_event_handler(event):
    print(event.raw_text)
    print(event.chat.username)
    list = event.raw_text.split(' ')
    print("========================>" + event.chat.username)
    print("========================>" + event.chat_id == -1001329310076)
    try:
        NOW = datetime.now()
        # 解析数据
        list_of_lines = event.raw_text.split('\n')

        list_of_strings = []

        final_list = []
        assetPair = list_of_lines[0].split(' ')[2]
        asset = assetPair.split('/')[0]
        assetBase = assetPair.split('/')[1]
        price = list_of_lines[1].split(' ')[1]
        _volume = list_of_lines[2].split(' ')[1]
        volume = list_of_lines[2].split(' ')[1].replace(',', '')
        priceIncr = list_of_lines[3].split(' ')[2]
        volumeIncr = list_of_lines[4].split(' ')[2].replace(',', '')
        ex = list_of_lines[6].split(' ')[2].replace(':', '')
        print("-----------------------------------------")
        print(assetPair + " " + asset + " " + assetBase + " " + str(price) + " " + str(volume))
        # print(priceIncr + " " + volumeIncr + " " + ex )

        monitor = Monitor(asset_pair=assetPair, asset=asset, asset_base=assetBase
                          , price=price, volume=volume, price_incr=priceIncr, volume_incr=volumeIncr, ex=ex,
                          updated_at=NOW)
        session.add(monitor)

        session.commit()

        print("assetPair:" + assetPair)
        # 初始化 es
        es = Elasticsearch("192.168.1.32")

        doc = {
            # 'id': tweet.id, 

            'asset_pair': assetPair,
            'price': float(price),
            'asset': asset,
            'volume': float(volume),
            'asset_base': assetBase,
            'price_incr': float(priceIncr),
            'volume_incr': float(volumeIncr),
            'ex': ex,
            'timestamp': time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        }
        logging.info(doc)

        res = es.index(index="public_tetlthon3", body=doc)
        logging.info("es result=" + res['result'])

        print(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()))
        mail_contents = event.raw_text.replace("Set custom Alerts: CoinTrendz.com", "")
        mail_subject = ex + " " + asset + " " + _volume + " " + assetBase
        ret = session.query(Monitor).filter(Monitor.asset == asset).filter(
            Monitor.updated_at >= NOW - timedelta(days=7)).count()
        ret2 = session.query(Monitor).filter(Monitor.asset_pair == assetPair).filter(
            Monitor.updated_at >= NOW - timedelta(days=30)).all()

        mail_contents = mail_contents + "\n"
        for i in ret2:
            mail_contents = mail_contents + '{:.8f}'.format(i.price) + " " + str(i.updated_at) + "\n"
            print(i.id, i.asset_pair, '{:.8f}'.format(i.price), i.updated_at)

        print("ret_count:" + str(ret))
        if ret > 3:
            sendMail(mail_subject, mail_contents)
            return

        if assetBase == 'USDT':

            if float(volume) < 10000000:
                print('Return:USDT:' + volume)
                return
            pass

        if assetBase == 'BTC':
            if float(volume) < 1000:
                print('Return:BTC:' + volume)
                return
            pass

        if assetBase == 'ETH':
            if float(volume) < 10000:
                print('Return:ETH:' + volume)
                return
            pass

        sendMail(mail_subject, mail_contents)
    except Exception as e:
        session.rollback()
        print("Error:" + str(e))
        logging.error("Error:" + str(e))


session.close()
client.start()
client.run_until_disconnected()
