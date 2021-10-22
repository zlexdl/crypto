
from binance.client import Client
import time
from config import global_config
from util import send_pushplus

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker

engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class BinanceCoins(Base):
    __tablename__ = "binance_coins"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    symbol = Column(String(50), nullable=True)
    price = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


while True:


    print(datetime.now())
    try:

        # create the Binance client, no need for api key
        client = Client("", "")

        datas = client.get_all_tickers()
        for data in datas:

            currency = data['symbol']
            price = data['price']
            if session.query(BinanceCoins).filter(BinanceCoins.symbol == currency).count() == 0:
                print(currency)
                binanceCoins = BinanceCoins(
                    symbol=currency
                    , price=price)

                session.add(binanceCoins)
                session.commit()
                subject = '币安将要新上交易对: ' + currency
                content = '币安将要新上交易对: ' + currency
                # sendMail(subject, content)
                send_pushplus(subject, content, '002')

    except Exception as e:
        session.rollback()
        print("sleep 3s")
        time.sleep(3)
        continue
    print("sleep 60s")
    time.sleep(60)

print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")