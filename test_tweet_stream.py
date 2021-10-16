import tweepy
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import wget
import os
from config import global_config
auth = tweepy.OAuthHandler("O8yZNzfoelt7fagdXkacsOXp7", "S9CCYUZ7GVq2VaPUB5iW5QnRnLyDPtpiS0L4SawNuIpvegiBYJ")
auth.set_access_token("112694900-gMcMQmgU1chzqhwuf58sRYqwEikZ76XCJBaQHrDV", "yTj1h4trMOf39NdXuQ4DwHoQo1cYmzrVJziN41hHWQXi3")
IMAGES_FOLDER = "./images/"
api = tweepy.API(auth)

def send_mail(tweet):
    mail_host = global_config.getRaw('mail', 'mail_host')
    mail_user = global_config.getRaw('mail', 'mail_user')
    mail_pass = global_config.getRaw('mail', 'mail_pass')

    sender = 'bsv_whale_alert@126.com'
    receivers = ['6585852@qq.com', '39644849@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message = MIMEMultipart()

    message['From'] = "whale_alert<bsv_whale_alert@126.com>"
    message['To'] = "6585852@qq.com, 39644849@qq.com"
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


class MyStreamListener(tweepy.StreamListener):
    #重写 on_status
    def on_status(self, status):
        if status.author.id == api.get_user('CryptoFaibik').id:
            send_mail(status)
            print(status.text)
        # status 是一个对象，里面包含了该条推文的所有字段，比如推文内容、点赞数、评论数、作者id、作者昵称、作者粉丝数等等


    # 当流媒体出错时被调用，如：身份验证失败、网络错误等等
    def on_error(self, status_code):
        if status_code == 420:
            return False #returning False in on_error disconnects the stream

# 实例化
myStreamListener = MyStreamListener()
# 身份验证，绑定监听流媒体
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
# --- 监听关键词Python相关的推文
# myStream.filter(track=['python'])
# --- 关注某推特用户，只能通过ID
myStream.filter(follow=[str(api.get_user('CryptoFaibik').id)])
# myStream.filter(follow=[str(api.get_user('TheCryptoVyom').id)])
# myStream.filter(follow=[str(api.get_user('WhaleBotPumps').id)])
# --- 支持异步，参数is_async，推荐使用异步形式
# myStream.filter(track=['BTC'], is_async=True)

# 关闭流媒体的监听
myStream.disconnect()