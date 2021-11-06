import logging

from pycoingecko import CoinGeckoAPI
import smtplib
import time
import json
import urllib.request
import math

import pymysql

from util import send_pushplus
from email.mime.text import MIMEText
from email.header import Header
from config import global_config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine(global_config.getRaw('db', 'hwdb_db_url'))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class GeckoCoinInfo(Base):
    __tablename__ = "gecko_coin_info"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    symbol = Column(String(50), nullable=True)
    name = Column(String(50), nullable=True)
    current_price = Column(Float, nullable=True)
    market_cap = Column(BigInteger, nullable=True)
    total_volume = Column(Float, nullable=True)
    total_supply = Column(Float, nullable=True)
    max_supply = Column(Float, nullable=True)
    ath = Column(Float, nullable=True)
    atl = Column(Float, nullable=True)
    times = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = Column(DateTime, default=datetime.now)


while True:

    print(datetime.now())
    try:

        cg = CoinGeckoAPI()
        count = cg.get_global()['active_cryptocurrencies']
        for i in range(1, math.ceil(count / 250)):

            # cg.get_coins_markets('usd', order='TRUST_SCORE_ASC', per_page=100, page=103)
            datas = cg.get_coins_markets('usd', order='TRUST_SCORE_DESC', per_page=250, page=i)
            for data in datas:
                symbol = data['symbol']
                name = data['name'][0:49]
                current_price = data['current_price']
                market_cap = data['market_cap']
                fully_diluted_valuation = data['fully_diluted_valuation']
                total_volume = data['total_volume']
                total_supply = data['total_supply']
                max_supply = data['max_supply']
                ath = data['ath']
                atl = data['atl']
                roi = data['roi']
                times = 0
                if roi is not None:
                    times = roi['times']

                try:
                    if session.query(GeckoCoinInfo).filter(GeckoCoinInfo.symbol == symbol).count() == 0:

                        geckoCoinInfo = GeckoCoinInfo(
                            symbol=symbol
                            , name=name
                            , current_price=current_price
                            , market_cap=market_cap
                            , total_volume=total_volume
                            , total_supply=total_supply
                            , max_supply=max_supply
                            , ath=ath
                            , atl=atl
                            , times=times)
                        # print("insert:" + symbol)
                        session.add(geckoCoinInfo)
                        session.commit()
                        price = '{:.18f}'.format(current_price)
                        max_supply = str('{:,}'.format(max_supply))
                        total_supply = str('{:,}'.format(total_supply))
                        subject = 'Gecko New Coin: ' + symbol
                        content = '<table><thead><tr><th></th><th></th></tr></thead><tbody><tr><td>name：</td><td>{}</td></tr><tr><td>symbol：</td><td>{}</td></tr><tr><td>最大供应量：</td><td>{}</td></tr><tr><td>总供应量：</td><td>{}</td></tr><tr><td>价格(U)：</td><td>{}</td></tr></tbody></table>'.format(
                            name, symbol, max_supply, total_supply, price)
                        # sendMail(subject, content)
                        send_pushplus(subject, content, '002')
                    else:
                        geckoCoinInfo = session.query(GeckoCoinInfo).filter(GeckoCoinInfo.symbol == symbol)
                        geckoCoinInfo.update({
                            "symbol": symbol
                            , "name": name
                            , "current_price": current_price
                            , "market_cap": market_cap
                            , "total_volume": total_volume
                            , "total_supply": total_supply
                            , "max_supply": max_supply
                            , "ath": ath
                            , "atl": atl
                            , "times": times})
                        # print("update:" + symbol)
                        session.commit()
                except Exception as e:
                    session.rollback()
                    print("Error0: " + str(e))
                    logging.error("Error0: " + str(e))
                    continue


            print("sleep 1s")
            time.sleep(1)
    except Exception as e:
        session.rollback()
        print("Error: " + str(e))
        print("sleep 300s")
        time.sleep(300)
        continue
    print("sleep 300s")
    time.sleep(300)
print("@@@@@@@@@@@@@@@@@@@@END@@@@@@@@@@@@@@@@@@@@@@")
