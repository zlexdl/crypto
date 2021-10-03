from telethon import TelegramClient, events, sync

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(filename='../logs/cryptoCove.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT,
                    encoding='utf-8')

api_id = 7928011
api_hash = 'b74852d9349c2b9b5f5a287ef1120733'

phone_number = '+8618242025966'

# client = TelegramClient(phone_number, api_id, api_hash, proxy=("HTTP", 'localhost', 10809))
client = TelegramClient(phone_number, api_id, api_hash)
print("1")
client.start()
print("2")
print(client.get_me())


@client.on(events.NewMessage(chats='CryptoCovePremium'))
# @client.on(events.NewMessage(chats='test_zlexdl'))
async def my_event_handler(event):
    print("CryptoCovePremium start")
    print(event.raw_text)

    # 发邮件 第三方 SMTP 服务
    mail_host = "smtp.126.com"  # 设置服务器
    mail_user = "bsv_whale_alert"  # 用户名
    mail_pass = "FFUNDLIEMVWJDCNV"  # 口令

    sender = 'bsv_whale_alert@126.com'
    receivers = ['frm5966@dingtalk.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText(event.raw_text, 'plain', 'utf-8')
    message['From'] = "bsv_whale_alert<bsv_whale_alert@126.com>"
    message['To'] = "zlexdl<frm5966@dingtalk.com>"

    subject = event.raw_text
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


client.start()
client.run_until_disconnected()
