import tweepy
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import wget
import os
from util import send_pushplus

from config import global_config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
engine = create_engine(global_config.getRaw('db', 'vultr_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='logs/test_tweet_stream.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT,
                    encoding='utf-8')


auth = tweepy.OAuthHandler(global_config.getRaw('twitter', 'consumer_key'),
                           global_config.getRaw('twitter', 'consumer_secret'))
auth.set_access_token(global_config.getRaw('twitter', 'key'),
                      global_config.getRaw('twitter', 'secret'))

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

IMAGES_FOLDER = "./images/"


class TwitterNotification(Base):
    __tablename__ = "twitter_notification"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    twitter_name = Column(String(50), nullable=True)
    email_address = Column(String(50), nullable=True)
    switch = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


def send_mail(tweet, to):
    mail_host = global_config.getRaw('mail', 'mail_host')
    mail_user = global_config.getRaw('mail', 'mail_user')
    mail_pass = global_config.getRaw('mail', 'mail_pass')

    sender = 'bsv_whale_alert@126.com'
    receivers = [to]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()

    message['From'] = "alert<bsv_whale_alert@126.com>"
    message['To'] = to
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
        logging.info("邮件发送开始")
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())

        logging.info("邮件发送成功")
    except smtplib.SMTPException:
        logging.info("Error: 无法发送邮件")



class MyStreamListener(tweepy.StreamListener):
    #重写 on_status
    def on_status(self, status):
        logging.info(status.text)
        logging.info(status.author.id)


        datas = session.query(TwitterNotification).filter(TwitterNotification.twitter_name == api.get_user(status.author.id).screen_name).all()
        for data in datas:
            obj = getDictFromObj_nr(data)
            email_address = obj['email_address']
            logging.info(email_address)
            send_pushplus(str(status.author.id), status.text, 'TW001')
            # send_mail(status, email_address)

        # if status.author.id == api.get_user('zlexdl').id:
        #     send_mail(status, email_address)
        #     print(status.text)

        # if status.author.id == api.get_user('WhaleBotPumps').id:
        #     send_mail(status)
            # print(status.text)
        # status 是一个对象，里面包含了该条推文的所有字段，比如推文内容、点赞数、评论数、作者id、作者昵称、作者粉丝数等等


    # 当流媒体出错时被调用，如：身份验证失败、网络错误等等
    def on_error(self, status_code):
        if status_code == 420:
            return False #returning False in on_error disconnects the stream

def retry():
    try:

        # 实例化
        myStreamListener = MyStreamListener()
        logging.info("start")

        # 身份验证，绑定监听流媒体
        myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
        # --- 监听关键词Python相关的推文
        # myStream.filter(track=['python'])
        # --- 关注某推特用户，只能通过ID
        # follow_list = [str(api.get_user('zlexdl').id), str(api.get_user('WhaleBotPumps').id), str(api.get_user('TheCryptoVyom').id), str(api.get_user('TraderWisdom').id)]
        follow_list = get_follow_list()
        myStream.filter(follow=follow_list)
        print("start")
        # myStream.filter(follow=[str(api.get_user('TheCryptoVyom').id)])
        # myStream.filter(follow=[str(api.get_user('WhaleBotPumps').id)])
        # --- 支持异步，参数is_async，推荐使用异步形式
        # myStream.filter(track=['BTC'], is_async=True)
        logging.info("filter")
        # 关闭流媒体的监听
        myStream.disconnect()
        logging.info("disconnect")
    except Exception as e:
        logging.info("Error: " + str(e))
        retry()

def getDictFromObj_nr(obj):
    return_dict = {}
    if isinstance(obj, TwitterNotification):
        for key in obj.__dict__:
            if key.startswith('_'): continue
            return_dict[key] = getattr(obj, key)
    return return_dict




# print(str(api.get_user("zlexdl").id))
def get_follow_list():
    datas = session.query(TwitterNotification).all()
    follow_list = []
    for data in datas:
        obj = getDictFromObj_nr(data)
        twitter_name = obj['twitter_name']
        logging.info(obj['twitter_name'])

        twitter_id = str(api.get_user(twitter_name).id)
        logging.info(api.get_user(twitter_id).screen_name)
        if twitter_id not in follow_list:
            follow_list.append(twitter_id)

    logging.info(follow_list)
    return follow_list


# get_follow_list()
retry()