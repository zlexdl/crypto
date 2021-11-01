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
from util import send_pushplus

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

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# user = api.get_user('CryptoNewton')
# public_tweets = api.user_timeline(user.id)


def send_mail(tweet):
    mail_host = global_config.getRaw('mail', 'mail_host')
    mail_user = global_config.getRaw('mail', 'mail_user')
    mail_pass = global_config.getRaw('mail', 'mail_pass')

    sender = 'bsv_whale_alert@126.com'
    receivers = ['6585852@qq.com', '393899161@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()

    message['From'] = "TW<bsv_whale_alert@126.com>"
    message['To'] = "6585852@qq.com, 393899161@qq.com"
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

        zlexdl = api.user_timeline(api.get_user('zlexdl').id, count=3)
        CryptoFaibik = api.user_timeline(api.get_user('CryptoFaibik').id, count=3)
        RadioCacaNFT = api.user_timeline(api.get_user('RadioCacaNFT').id, count=3)
        bsc_daily = api.user_timeline(api.get_user('bsc_daily').id, count=3)
        bakery_swap = api.user_timeline(api.get_user('bakery_swap').id, count=3)
        VenusProtocol = api.user_timeline(api.get_user('VenusProtocol').id, count=3)
        cz_binance = api.user_timeline(api.get_user('cz_binance').id, count=3)
        Binance = api.user_timeline(api.get_user('Binance').id, count=3)
        TheBinanceNFT = api.user_timeline(api.get_user('TheBinanceNFT').id, count=3)
        ElemonGame = api.user_timeline(api.get_user('ElemonGame').id, count=3)
        top7ico = api.user_timeline(api.get_user('top7ico').id, count=3)
        print("---------------------public_tweets")
        public_tweets = zlexdl + CryptoFaibik + RadioCacaNFT + bsc_daily + bakery_swap + VenusProtocol + cz_binance + Binance + TheBinanceNFT + ElemonGame + top7ico

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
            # send_mail(tweet)
            send_pushplus(tweet.user.screen_name, tweet.text, 'TW001')

    print("time.sleep(300) start time=" + str(datetime.utcnow()))
    time.sleep(300)
    logging.info("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
    print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
