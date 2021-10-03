import json
import re
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, Boolean, Date, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import text
from config import global_config

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='logs/read_coin_info.log', level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')

engine = create_engine(global_config.getRaw('config', 'db_url'))
Base = declarative_base()


class Crowdsales(Base):
    __tablename__ = "crowdsales"  # 数据库中保存的表名字
    id = Column(Integer, index=True, primary_key=True)

    key = Column(String(20), nullable=True)
    type = Column(String(20), nullable=True)
    start = Column(String(20), nullable=True)
    end = Column(String(20), nullable=True)
    showOnlyMonth = Column(String(20), nullable=True)
    tokenIssue = Column(String(100), nullable=True)
    minMaxPersonalCap = Column(String(20), nullable=True)
    allocationSize = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True)
    ieoExchangeKey = Column(String(20), nullable=True)
    idoPlatformKey = Column(String(20), nullable=True)
    UsdPrice = Column(Float, nullable=True)
    numberOfParticipants = Column(Float, nullable=True)
    isCalculateRoiTable = Column(String(5), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


def read_json_data(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8') as load_f:

        load_dict = json.load(load_f)
        Session = sessionmaker(bind=engine)

        session = Session()

        count = 0
        for m in load_dict['data']:
            key = str(m)
            for n in load_dict['data'][m]:

                try:
                    coin = Crowdsales(key=key
                                      , type=n.get('type', '')
                                      , start=n.get('start', '')
                                      , end=n.get('end', '')
                                      , showOnlyMonth=n.get('showOnlyMonth', '')
                                      , tokenIssue=n.get('tokenIssue', '')
                                      , minMaxPersonalCap=n.get('minMaxPersonalCap', '')
                                      , allocationSize=n.get('allocationSize', 0)
                                      , status=n.get('status', '')
                                      , ieoExchangeKey=n.get('ieoExchangeKey', '')
                                      , idoPlatformKey=n.get('idoPlatformKey', '')
                                      , UsdPrice=n['price']['USD']
                                      , numberOfParticipants=n.get('numberOfParticipants', 0)
                                      , isCalculateRoiTable=n.get('isCalculateRoiTable', '')
                                      )

                    session.add(coin)
                    session.commit()
                except Exception as err:
                    session.rollback()
                    print(key)
                    # print('count=' + str(count))
                    print(err)
        session.close()
        print('count=' + str(count))


if __name__ == '__main__':
    print('start')

    read_json_data("data/crowdsales.json")
