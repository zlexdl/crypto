import tweepy
import time
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import wget
import os

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
IMAGES_FOLDER = "./images/"
utcTime = datetime.utcnow()
print(utcTime)

logging.basicConfig(filename='logs/getTwitter.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT,
                    encoding='utf-8')

auth = tweepy.OAuthHandler("O8yZNzfoelt7fagdXkacsOXp7", "S9CCYUZ7GVq2VaPUB5iW5QnRnLyDPtpiS0L4SawNuIpvegiBYJ")
auth.set_access_token("112694900-gMcMQmgU1chzqhwuf58sRYqwEikZ76XCJBaQHrDV",
                      "yTj1h4trMOf39NdXuQ4DwHoQo1cYmzrVJziN41hHWQXi3")

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# user = api.get_user('CryptoNewton')
# public_tweets = api.user_timeline(user.id)


def send_mail(tweet):
    global text
    mail_host = "smtp.126.com"  # 设置服务器
    mail_user = "bsv_whale_alert"  # 用户名
    mail_pass = "FFUNDLIEMVWJDCNV"  # 口令
    sender = 'bsv_whale_alert@126.com'
    receivers = ['frm5966@dingtalk.com', 'd875x9g@dingtalk.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()

    message['From'] = "bsv_whale_alert<bsv_whale_alert@126.com>"
    message['To'] = "zlexdl<frm5966@dingtalk.com>, d875x9g@dingtalk.com"
    subject = tweet.user.screen_name
    message['Subject'] = Header(subject, 'utf-8')
    text = MIMEText(tweet.text)
    message.attach(text)
    media = tweet.entities.get('media', [])
    if len(media) > 0:
        image_url = media[0]['media_url']
        wget.download(image_url, out=IMAGES_FOLDER)
        logging.info("---------------------" + image_url)
        (path, filename) = os.path.split(image_url)
        with open(IMAGES_FOLDER + filename, 'rb') as f:
            img_data = f.read()

        image = MIMEImage(img_data, name=filename)
        message.attach(image)
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())

        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


while True:
    print("@@@@@@@@@@@@@@@@@@@@Start@@@@@@@@@@@@@@@@@@@@@@")
    logging.info("@@@@@@@@@@@@@@@@@@@@Start@@@@@@@@@@@@@@@@@@@@@@")
    logging.info(datetime.utcnow())

    public_tweets = []

    try:
        # public_tweets = api.home_timeline(count=50)
        # public_tweets = api.list_timeline(list_id=1413685290284163076,count=50)

        user = api.get_user('CryptoFaibik')
        public_tweets = api.user_timeline(user.id)
    except Exception as e:
        print("sleep 60s")
        time.sleep(60)
        continue

    # user = api.get_user('CryptoNewton')
    # public_tweets = api.user_timeline(user.id)

    # utcTime = datetime.utcnow()

    for tweet in public_tweets:

        logging.info("id=" + str(tweet.id))
        logging.info("created_at=" + str(tweet.created_at))
        logging.info("tweet---------------------")
        logging.info(tweet.text)
        logging.info("tweet---------------------")
        logging.info("screen_name=" + tweet.user.screen_name)
        utcTime_minutes = datetime.utcnow() - timedelta(minutes=5)
        print(tweet.text)
        print("---------------------")
        print(tweet.created_at)
        print(utcTime_minutes)
        print("---------------------")
        # send_mail(tweet)
        if tweet.created_at >= utcTime_minutes:

            send_mail(tweet)

    print("time.sleep(300) start time=" + str(datetime.utcnow()))
    time.sleep(300)
    logging.info("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
    print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
