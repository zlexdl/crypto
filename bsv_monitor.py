# coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from config import global_config
import datetime
import time
import json
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import traceback
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='logs/bsv_monitor.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT,
                    encoding='utf-8')

engine = create_engine(global_config.getRaw('db', 'bsv_db_url'))
Base = declarative_base()


class Address(Base):
    __tablename__ = "address"  # 数据库中保存的表名字

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    address = Column(String(50), index=True, nullable=False)
    balance = Column(BigInteger, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now)


if __name__ == "__main__":
    # Base.metadata.create_all(engine)
    # Base.metadata.drop_all(engine)

    while True:

        print("@@@@@@@@@@@@@@@@@@@@Start@@@@@@@@@@@@@@@@@@@@@@ ")

        Session = sessionmaker(bind=engine)

        session = Session()

        ret = session.query(Address).all()

        for i in ret:
            print(i.id, i.address, i.balance)

            url = 'https://apiv2.metasv.com/address/' + i.address + '/balance'

            try:
                f = urllib.request.urlopen(url)
            except Exception as e:
                print("sleep 60s")
                time.sleep(60)
                continue

            res_json = f.read().decode('utf8')
            print(res_json)
            text = json.loads(res_json)
            print(text)
            balance = text['confirmed'] // 100000000
            print("new_balance=" + str(balance))
            old_balance = i.balance

            print("old_balance=" + str(old_balance))

            diff = abs(balance - old_balance)
            print("diff=" + str(diff))

            if diff > 3999 or ('112QeSdnn9MYt5CtYjC6id3NUoVZBJ851R' == i.address and diff > 1):

                # data_dic = {
                #     'chat_id':'@zlexdl_test',
                #     'text':'BSV whale balance change warning\naddress:' + i.address + '\nbefore:' + str(i.balance) + '\nafter   :' + str(balance)
                # }

                # data_parse = parse.urlencode(data_dic)
                # data_b = data_parse.encode('utf-8')

                # print(data_dic)
                # url1 = 'https://api.telegram.org/bot1894161385:AAE2dNmZC9GaiBuTmL0-SDEJnL0QzBywRn8/sendMessage'
                # print(url1)

                # proxy_host = 'localhost:10809'    # host and port of your proxy

                # req = urlrequest.Request(url1)
                # req.set_proxy(proxy_host, 'http')

                # response = urlrequest.urlopen(req, data=data_b)
                # print(response.read().decode('utf8'))

                # 第三方 SMTP 服务
                mail_host = global_config.getRaw('mail', 'mail_host')
                mail_user = global_config.getRaw('mail', 'mail_user')
                mail_pass = global_config.getRaw('mail', 'mail_pass')

                symbol = "+" if balance > old_balance else "-"

                sender = 'bsv_whale_alert@126.com'
                receivers = ['zlexdl@163.com', 'jiangdi_li@126.com', 'lzjjxljaljt@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
                # receivers = ['zlexdl@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
                content = 'BSV whale balance change warning<br><table border="1"><tr><td>address:</td><td>' + i.address + '</td></tr><tr><td>Before:</td><td>' + '{:,}'.format(
                    old_balance) + ' BSV</td></tr><tr><td>After   :</td><td>' + '{:,}'.format(
                    balance) + ' BSV</td></tr><tr><td>Difference:</td><td>' + symbol + '{:,}'.format(
                    diff) + ' BSV</td></tr></table>'
                message = MIMEText(content, 'html', 'utf-8')
                message['From'] = "bsv_whale_alert<bsv_whale_alert@126.com>"
                message[
                    'To'] = "zlexdl<zlexdl@163.com>, jiangdi_li<jiangdi_li@126.com>, lzjjxljaljt<lzjjxljaljt@163.com>"
                # message['To'] =  "zlexdl<zlexdl@163.com>"

                subject = i.address[0:4] + " " + str(diff) + " " + str(balance)
                message['Subject'] = Header(subject, 'utf-8')

                try:
                    smtpObj = smtplib.SMTP()
                    smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
                    smtpObj.login(mail_user, mail_pass)
                    smtpObj.sendmail(sender, receivers, message.as_string())
                    print("邮件发送成功" + subject)
                    logging.info("邮件发送成功" + subject)
                except smtplib.SMTPException as e:
                    print("Error: 无法发送邮件")
                    logging.error("邮件发送成功" + subject)
                    traceback.print_exc()

            if diff > 0:
                print("update balance" + str(balance))
                logging.info("update balance" + str(balance))
                session.query(Address).filter(Address.address == i.address).update({"balance": balance})

        session.commit()

        # session.commit()

        session.close()

        time.sleep(300)
        print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")

        # address = Address(name="1", address="1A9nhwLngEyf3Jzycvb9GeG4ayBv5m5zKc", balance=0)
        # session.add(address)
        # address = Address(name="2", address="13LGR1QjYkdi4adZV1Go6cQTxFYjquhS1y", balance=0)
        # session.add(address)
        # address = Address(name="3", address="112QeSdnn9MYt5CtYjC6id3NUoVZBJ851R", balance=0)
        # session.add(address)
        # address = Address(name="4", address="17ve2EPbtvUaQykXvTBhvKHX9e9uS2kFi5", balance=0)
        # session.add(address)
        # address = Address(name="5", address="197APpASEVuAfDKf8BKdGEGWY2XD8cEQmx", balance=0)
        # session.add(address)
        # address = Address(name="6", address="1AcpaEcJACmAEniQ1QfeLEGR986b9Bff5Y", balance=0)
        # session.add(address)
        # address = Address(name="7", address="1NhiBcHBdiJxggEXEHP8DURnaMgSWbtL7B", balance=0)
        # session.add(address)
        # address = Address(name="8", address="13Zp4xBptPZiGDu8Bur3L4F1QK2ZARcpiE", balance=0)
        # session.add(address)
        # address = Address(name="9", address="1H9cNzaWoESPurNMPx2zGWcjbkUWWiXKMd", balance=0)
        # session.add(address)
        # address = Address(name="10", address="1M9esRZvPXxRfPiyREUi6NGBuLBevvmF8T", balance=0)
        # session.add(address)
        # address = Address(name="11", address="1JZzW9L59tHosrdco4zVrLiGV2pD72VUoF", balance=0)
        # session.add(address)
        # address = Address(name="12", address="3AcYRPHcMQeRx2JyVEYLG9oDEiy1qgsWka", balance=0)
        # session.add(address)
        # address = Address(name="13", address="1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF", balance=0)
        # session.add(address)
        # address = Address(name="14", address="1F884r9J2WKbu8wekebqqRcu1Bw1jiRXba", balance=0)
        # session.add(address)
        # address = Address(name="15", address="1Hw2k2iuhzcrA1Rvm6EuCoiCSp7Sc6mdrv", balance=0)
        # session.add(address)
        # address = Address(name="16", address="1C9HmxACTUqiGLn5pMHzRXciJDpKYBxLuM", balance=0)
        # session.add(address)
        # address = Address(name="17", address="1EkkGXR7dTbZbrKFKoe6YEP4gj4GzMeKvw", balance=0)
        # session.add(address)
        # address = Address(name="18", address="1CW7X41YBfy73UfVJsATkt4d6V67uxQ9L2", balance=0)
        # session.add(address)
        # address = Address(name="19", address="1MYVcPwcJJEXMihEa9Cnx1eBAmps9ycaiJ", balance=0)
        # session.add(address)
        # address = Address(name="20", address="13rdDs9iWpsLYsmXRxkUPDwZCU7xrPr6Mt", balance=0)
        # session.add(address)
