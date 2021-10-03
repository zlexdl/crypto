import json
import re
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Date, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import text
from config import global_config

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='logs/read_coin_info.log', level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')

engine = create_engine(global_config.getRaw('config', 'db_url'))
Base = declarative_base()


class Coins(Base):
    __tablename__ = "coins"  # 数据库中保存的表名字
    id = Column(Integer, index=True, primary_key=True)
    rank = Column(Integer, nullable=True)
    key = Column(String(20), nullable=True)
    name = Column(String(50), nullable=True)
    symbol = Column(String(20), nullable=True)
    type = Column(String(20), nullable=True)
    marketCap = Column(Float, nullable=True)
    availableSupply = Column(Float, nullable=True)
    fullyDilutedMarketCap = Column(Float, nullable=True)
    totalSupply = Column(Float, nullable=True)
    icon = Column(String(100), nullable=True)
    image = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    athPrice = Column(Float, nullable=True)
    athPriceDate = Column(Date, nullable=True)

    updated_at = Column(DateTime, default=datetime.now)


def read_json_data(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as load_f:

        load_dict = json.load(load_f)
        Session = sessionmaker(bind=engine)

        session = Session()

        count = 0
        for m in load_dict['data']:

            try:
                coin = Coins(rank=m['rank']
                             , key=m['key']
                             , name=m['name']
                             , symbol=m['symbol']
                             , type=m['type']
                             , marketCap=m['marketCap']
                             , availableSupply=m['availableSupply']
                             , fullyDilutedMarketCap=m['fullyDilutedMarketCap']
                             , totalSupply=m['totalSupply']
                             , icon=m['icon']
                             , image=m['image']
                             , category=m['category']
                             , athPrice=m['athPrice']['USD']
                             , athPriceDate=m['athPrice']['date']
                             )

                session.add(coin)
                session.commit()
            except Exception as err:
                session.rollback()
                print(m['key'])
                # print('count=' + str(count))
                print(err)
        session.close()
        print('count=' + str(count))


if __name__ == '__main__':
    print('start')

    read_json_data("data/coins.json")
