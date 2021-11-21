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
from config import global_config
from util import send_pushplus, send_pushplus_wx
import translators as ts

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
IMAGES_FOLDER = "./images/"
utcTime = datetime.utcnow()
print(utcTime)

logging.basicConfig(filename='logs/getTwitter.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT,
                    encoding='utf-8')

auth = tweepy.OAuthHandler(global_config.getRaw('twitter', 'consumer_key'),
                           global_config.getRaw('twitter', 'consumer_secret'))
auth.set_access_token(global_config.getRaw('twitter', 'key'),
                      global_config.getRaw('twitter', 'secret'))

api = tweepy.API(auth)


# user = api.get_user('CryptoNewton')
# public_tweets = api.user_timeline(user.id)


def send_mail(tweet):
    mail_host = global_config.getRaw('mail', 'mail_host')
    mail_user = global_config.getRaw('mail', 'mail_user')
    mail_pass = global_config.getRaw('mail', 'mail_pass')

    # '393899161@qq.com'
    sender = 'bsv_whale_alert@126.com'
    receivers = ['6585852@qq.com', '393899161@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()

    message['From'] = "TW<bsv_whale_alert@126.com>"
    message['To'] = "6585852@qq.com, 393899161@qq.com"
    subject = tweet.user.screen_name
    message['Subject'] = Header(subject, 'utf-8')
    text = MIMEText(tweet.text) # .extended_tweet['full_text']

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

        # zlexdl = api.user_timeline(screen_name='zlexdl', count=3, tweet_mode='extended')
        CryptoFaibik = api.user_timeline(screen_name='CryptoFaibik', count=3, tweet_mode='extended')
        ElemonGame = api.user_timeline(screen_name='ElemonGame', count=3, tweet_mode='extended')
        top7ico = api.user_timeline(screen_name='top7ico', count=3, tweet_mode='extended')
        ZssBecker = api.user_timeline(screen_name='ZssBecker', count=3, tweet_mode='extended')
        HoppyMeme = api.user_timeline(screen_name='HoppyMeme', count=3, tweet_mode='extended')
        Aleph__Zero = api.user_timeline(screen_name='Aleph__Zero', count=3, tweet_mode='extended')
        Bitpan8 = api.user_timeline(screen_name='Bitpan8', count=3, tweet_mode='extended')
        RaccoonHKG = api.user_timeline(screen_name='RaccoonHKG', count=3, tweet_mode='extended')
        print("---------------------public_tweets")
        public_tweets = CryptoFaibik + ElemonGame + top7ico + ZssBecker + HoppyMeme + Aleph__Zero + RaccoonHKG

    except Exception as e:
        print(str(e))
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
        logging.info(tweet.full_text)
        logging.info("tweet---------------------"+ tweet.full_text)
        logging.info("screen_name=" + tweet.user.screen_name)
        utcTime_minutes = datetime.utcnow() - timedelta(minutes=5)
        print(tweet.full_text)
        print("---------------------")
        print(tweet.created_at.replace(tzinfo=None))
        print(utcTime_minutes.replace(microsecond=0))
        print("---------------------")
        # send_mail(tweet)
        if tweet.created_at.replace(tzinfo=None) >= utcTime_minutes.replace(microsecond=0):
            # send_mail(tweet)
            tran = ''
            try:
                tran = ts.google(tweet.full_text, from_language='en', to_language='zh-CN')
            except Exception as e:
                tran = ''
                print(str(e))
            text = tweet.full_text + '\n\n-----------------------\n\n' + tran
            # send_pushplus(tweet.user.screen_name, text, 'TW001')
            send_pushplus_wx(tweet.user.screen_name, text.replace("\n", "\r\n"), 'dbzs')

    print("time.sleep(300) start time=" + str(datetime.utcnow()))
    time.sleep(300)
    logging.info("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
    print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
