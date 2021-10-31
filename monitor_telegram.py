from telethon import TelegramClient, events, sync
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import time
from config import global_config
from monitor_logger import logging
from telethon.tl.types import PeerChannel
from util import send_pushplus

is_test = 0
WHALE_SUSHI = 'sushiwhale'
WHALE_UNI = 'uniwhales'
WHALE_PANCAKE = 'pancakewhales'
WHALE_TEST = 'test_zlexdl'
PUMP_DETECTOR = 'cointrendz_pumpdetector'
CRYPTO_COVE_PREMIUM = 'CryptoCovePremium'
JIJIFABU_NOTICE00 = 'jijifabu_notice00'

engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class WhaleEth(Base):
    __tablename__ = "whale_eth"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    from_volume = Column(Float, nullable=True)
    to_volume = Column(Float, nullable=True)
    from_asset = Column(String(10), nullable=True)
    to_asset = Column(String(10), nullable=True)
    ex = Column(String(20), nullable=True)
    price = Column(Float, nullable=True)
    txn_type = Column(String(10), nullable=True)
    txn_href = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


class WhaleBsc(Base):
    __tablename__ = "whale_bsc"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    from_volume = Column(Float, nullable=True)
    to_volume = Column(Float, nullable=True)
    from_asset = Column(String(10), nullable=True)
    to_asset = Column(String(10), nullable=True)
    ex = Column(String(20), nullable=True)
    price = Column(Float, nullable=True)
    txn_type = Column(String(10), nullable=True)
    txn_href = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


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
    updated_at = Column(DateTime, default=datetime.now)


def read_message(telegram_message, flag):
    count = 0

    if isinstance(telegram_message, str):
        print('continue0=' + str(telegram_message))
        return
    if len(telegram_message) >= 10:
        try:
            index = 0
            for m in telegram_message:
                if m.find('Swap') >= 0:
                    from_volume = telegram_message[index + 1].replace(',', '')
                    from_asset = telegram_message[index + 2].replace('#', '')
                if m == 'for' or m == 'For':
                    to_volume = telegram_message[index + 1].replace(',', '')
                    to_asset = telegram_message[index + 2].replace('#', '')
                    price = float(re.findall(r"\d+\.?\d*", telegram_message[index + 4].split('\n')[0])[0])
                txn_type = ''
                if m == '#shrimp':
                    txn_type = 'shrimp'
                elif m == '#fish':
                    txn_type = 'fish'
                elif m == '#dolphin':
                    txn_type = 'dolphin'
                elif m == '#whale':
                    txn_type = 'whale'
                index = index + 1

            print("{},{},{},{},{},price:{}".format(from_volume, from_asset, to_volume, to_asset, txn_type,
                                                   price))

            if flag == WHALE_PANCAKE:
                if session.query(WhaleBsc).filter(WhaleBsc.from_asset == to_asset,
                                                  WhaleBsc.to_asset == from_asset).count() > 0:
                    whale = WhaleBsc(from_volume=-float(to_volume)
                                     , from_asset=to_asset
                                     , to_volume=-float(from_volume)
                                     , to_asset=from_asset
                                     , price=price
                                     , ex=flag
                                     , txn_type=txn_type)

                else:
                    whale = WhaleBsc(from_volume=from_volume
                                     , from_asset=from_asset
                                     , to_volume=to_volume
                                     , to_asset=to_asset
                                     , price=price
                                     , ex=flag
                                     , txn_type=txn_type)

            else:
                if session.query(WhaleEth).filter(WhaleEth.from_asset == to_asset,
                                                  WhaleEth.to_asset == from_asset).count() > 0:
                    whale = WhaleEth(from_volume=-float(to_volume)
                                     , from_asset=to_asset
                                     , to_volume=-float(from_volume)
                                     , to_asset=from_asset
                                     , price=price
                                     , ex=flag
                                     , txn_type=txn_type)
                else:
                    whale = WhaleEth(from_volume=from_volume
                                     , from_asset=from_asset
                                     , to_volume=to_volume
                                     , to_asset=to_asset
                                     , price=price
                                     , ex=flag
                                     , txn_type=txn_type)

            session.add(whale)
            session.commit()
        except Exception as err:
            session.rollback()
            print(err)
    session.close()


def sendMail(mail_subject, mail_contents):
    # 发邮件 第三方 SMTP 服务
    mail_host = global_config.getRaw('mail', 'mail_host')
    mail_user = global_config.getRaw('mail', 'mail_user')
    mail_pass = global_config.getRaw('mail', 'mail_pass')
    sender = global_config.getRaw('mail', 'sender')

    # dlwg10g@dingtalk.com 梨
    # btcbch2017@dingtalk.com bsv666
    # d875x9g@dingtalk.com 于
    # sangxiaomeng@dingtalk.com/ 327388224@qq.com C 哥
    # txy-87evmhmuw@dingtalk.com hanno
    message = MIMEText(mail_contents, 'plain', 'utf-8')
    message['From'] = global_config.getRaw('mail', 'from')
    message['Subject'] = Header(mail_subject, 'utf-8')

    if is_test == int(global_config.getRaw('mail', 'is_test')) or mail_subject == 'test':

        receivers = ['frm5966@dingtalk.com', '6585852@qq.com']
        message['To'] = "zlexdl<frm5966@dingtalk.com>, 6585852@qq.com"
    else:
        receivers = ['frm5966@dingtalk.com', 'txy-87evmhmuw@dingtalk.com', '327388224@qq.com', '6585852@qq.com',
                     '626188@qq.com',
                     'd875x9g@dingtalk.com', 'btcbch2017@dingtalk.com', 'dlwg10g@dingtalk.com']
        message['To'] = "frm5966@dingtalk.com,txy-87evmhmuw@dingtalk.com,327388224@qq.com," \
                        "6585852@qq.com,626188@qq.com, " \
                        "d875x9g@dingtalk.com," \
                        "btcbch2017@dingtalk.com, dlwg10g@dingtalk.com, "

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

def jijifabu_notice00(event):
    try:
        # 解析数据
        list_of_lines = event.raw_text.split('\n')

        list_of_strings = []

        final_list = []
        ex = list_of_lines[0]
        datetime = list_of_lines[1]

        send_pushplus(ex, event.raw_text, 'announcements')
    except Exception as e:
        print("Error:" + str(e))
        logging.error("Error:" + str(e))


def pump_detector(event):
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
        # 币安以外不发送
        if ex != "Binance":
            return
        print(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()))
        mail_contents = event.raw_text.replace("Set custom Alerts: CoinTrendz.com", "")
        mail_subject = ex + " " + asset + " " + _volume + " " + assetBase
        ret = session.query(Monitor).filter(Monitor.asset == asset).filter(
            Monitor.updated_at >= NOW - timedelta(days=7)).count()
        ret2 = session.query(Monitor).filter(Monitor.asset_pair == assetPair).filter(
            Monitor.updated_at >= NOW - timedelta(days=30)).all()

        mail_contents = mail_contents.replace("\n", "\r\n") + "\r\n"
        for i in ret2:
            mail_contents = mail_contents + '{:.8f}'.format(i.price) + " " + str(i.updated_at) + "\r\n"
            print(i.id, i.asset_pair, '{:.8f}'.format(i.price), i.updated_at)

        print("ret_count:" + str(ret))
        if ret > 3:
            # sendMail(mail_subject, mail_contents)
            send_pushplus(mail_subject, mail_contents, 'pump001')
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
        print('send_pushplus')
        # sendMail(mail_subject, mail_contents)
        send_pushplus(mail_subject, mail_contents, 'pump001')
    except Exception as e:
        session.rollback()
        print("Error:" + str(e))
        logging.error("Error:" + str(e))


api_id = global_config.getRaw('telegram_155', 'api_id')
api_hash = global_config.getRaw('telegram_155', 'api_hash')
phone_number = global_config.getRaw('telegram_155', 'phone_number')

client = TelegramClient(phone_number, api_id, api_hash)
print("1")
client.start()
print("2")
print(client.get_me())


async def my_event_handler(event):
    logging.info("Monitor whales start")
    logging.info(event.chat_id)
    print(event.raw_text)
    print(event.chat.username)

    if event.chat_id == -1001329310076:
        pump_detector(event)
        logging.info('test:' + event.raw_text)
        # sendMail('test', event.raw_text)
        send_pushplus('test', event.raw_text, 'pump001')
    elif event.chat.username == WHALE_TEST:
        raw_text = event.raw_text.split(' ')
        read_message(raw_text, WHALE_PANCAKE)
    elif event.chat.username in (WHALE_PANCAKE, WHALE_SUSHI, WHALE_UNI):
        raw_text = event.raw_text.split(' ')
        read_message(raw_text, event.chat.username)
    elif event.chat.username == PUMP_DETECTOR:
        pump_detector(event)
    elif event.chat.username == JIJIFABU_NOTICE00:
        jijifabu_notice00(event)
    elif event.chat_id == -1001385300019:
        logging.info('[VIP]COVE PREMIUM:' + event.raw_text)

        symbol = ''
        between = ''
        try:
            info = event.raw_text.split('\n\n')
            info1 = info[0]
            info2 = info[1]
            if info2.lower().find('buy between') >= 0:
                symbol = info1.split(' ')[1].replace('#', '')
                between = info2.lower().replace('buy between', '')
                title = '{}'.format(symbol)
                content = '{}在区间{}'.format(symbol, between)
                send_pushplus(title, content, 'VIP001')
        except Exception as e:
            print("Error:" + str(e))
            logging.error("Error:" + str(e))
        sendMail('[VIP]{}:{}'.format(symbol, between), event.raw_text)
    else:
        print("========================>Other")

    # mail_subject = event.raw_text
    # mail_contents = MIMEText(event.raw_text, 'plain', 'utf-8').as_string()
    #
    # sendMail(mail_subject, mail_contents)


client.add_event_handler(my_event_handler, events.NewMessage(chats=JIJIFABU_NOTICE00))
client.add_event_handler(my_event_handler, events.NewMessage(chats=WHALE_SUSHI))
client.add_event_handler(my_event_handler, events.NewMessage(chats=WHALE_UNI))
client.add_event_handler(my_event_handler, events.NewMessage(chats=WHALE_PANCAKE))

client.add_event_handler(my_event_handler, events.NewMessage(chats=PUMP_DETECTOR))
client.add_event_handler(my_event_handler, events.NewMessage(chats=[PeerChannel(-1001385300019)]))
client.add_event_handler(my_event_handler, events.NewMessage(chats=[PeerChannel(-1001329310076)]))

client.start()
client.run_until_disconnected()
