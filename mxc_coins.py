
import time
import json
import urllib.request
from config import global_config
from util import get_random_useragent, send_pushplus

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker


engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class MxcCoins(Base):
    __tablename__ = "mxc_coins"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    symbol = Column(String(50), nullable=True)
    name = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


while True:
    url = 'https://www.mxc.com/open/api/v2/market/coin/list'

    print(datetime.now())
    try:

        headers = {'User-Agent': get_random_useragent()}

        # 设置代理
        handler = urllib.request.ProxyHandler()
        opener = urllib.request.build_opener(handler)
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

            currency = data['currency']
            full_name = data['full_name']
            if session.query(MxcCoins).filter(MxcCoins.symbol == currency).count() == 0:
                print(currency)
                mxcCoins = MxcCoins(
                    symbol=currency
                    , name=full_name)

                session.add(mxcCoins)
                session.commit()
                subject = '抹茶将要新上币种: ' + currency
                content = '抹茶将要新上币种: ' + full_name
                # sendMail(subject, content)
                send_pushplus(subject, content, '002')

    except Exception as e:
        print("sleep 3s")
        time.sleep(3)
        continue
    print("sleep 5s")
    time.sleep(5)
    
print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")