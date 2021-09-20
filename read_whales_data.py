import json
import re
from datetime import datetime, timedelta
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import text

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='logs/read_json_data.log', level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT, encoding='utf-8')

engine = create_engine("mysql+pymysql://root:password@192.168.1.32:3306/hwdb?charset=utf8")
Base = declarative_base()


class WhaleEth(Base):
    __tablename__ = "whale_eth"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    from_volume = Column(Float, nullable=True)
    to_volume = Column(Float, nullable=True)
    from_asset = Column(String(10), nullable=True)
    to_asset = Column(String(10), nullable=True)
    ex = Column(String(10), nullable=True)
    price = Column(Float, nullable=True)
    txn_type = Column(String(10), nullable=True)
    txn_href = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


class WhaleBsc(Base):
    __tablename__ = "whale_bsc"  # 数据库中保存的表名字

    id = Column(Integer, index=True, primary_key=True)
    from_volume = Column(Float, nullable=True)
    to_volume = Column(Float, nullable=True)
    from_asset = Column(String(10), nullable=True)
    to_asset = Column(String(10), nullable=True)
    ex = Column(String(10), nullable=True)
    price = Column(Float, nullable=True)
    txn_type = Column(String(10), nullable=True)
    txn_href = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.now)


def read_json_data(jsonfile, flag):
    with open(jsonfile, 'r', encoding='utf-8') as load_f:

        load_dict = json.load(load_f)
        Session = sessionmaker(bind=engine)

        session = Session()

        count = 0
        for m in load_dict['messages']:
            msg_date = m['date']
            if isinstance(m['text'], str):
                print('continue0=' + str(m['text']))
                continue
            if len(m['text']) >= 10:
                try:
                    if isinstance(m['text'][0], dict):
                        print('continue1=' + str(m['text']))
                        continue
                    if m['text'][0].find('Swap') < 0:
                        print('continue2=' + str(m['text']))
                        continue
                    from_volume = m['text'][1]['text'].replace(',', '')
                    from_asset = m['text'][3]['text'].replace('#', '')
                    to_volume = m['text'][5]['text'].replace(',', '')
                    to_asset = m['text'][7]['text'].replace('#', '')
                    # price = m['text'][8].replace(r'\d+', '').replace('\n', '').replace('🦄', '').replace(',', '')
                    price = float(re.findall(r"\d+\.?\d*", m['text'][8])[0])
                    txn_type = ''
                    txn_href = ''
                    count = count + 1
                    for n in range(9, len(m['text']) - 1):
                        other = m['text'][n]
                        if isinstance(other, dict):
                            # count = count + 1
                            if other['text'] == '#shrimp':
                                txn_type = 'shrimp'
                            elif other['text'] == '#fish':
                                txn_type = 'fish'
                            elif other['text'] == '#dolphin':
                                txn_type = 'dolphin'
                            elif other['text'] == '#whale':
                                txn_type = 'whale'
                            elif 'href' in other:
                                if other['href'] != '':
                                    txn_href = other['href']
                            elif other['text'] == 'Etherscan':
                                txn_href = n['href']
                            # if txn_type == '':
                            #     print(m['text'])

                    print("{},{},{},{},{},{},price:{}".format(from_volume, from_asset, to_volume, to_asset, txn_type,
                                                              txn_href, price))

                    if flag == 'cake':
                        if session.query(WhaleBsc).filter(WhaleBsc.from_asset == to_asset,
                                                          WhaleBsc.to_asset == from_asset).count() > 0:
                            whale = WhaleBsc(from_volume=-float(to_volume)
                                             , from_asset=to_asset
                                             , to_volume=-float(from_volume)
                                             , to_asset=from_asset
                                             , price=price
                                             , ex=flag
                                             , txn_type=txn_type
                                             , txn_href=txn_href
                                             , updated_at=msg_date
                                             )
                        else:
                            whale = WhaleBsc(from_volume=from_volume
                                             , from_asset=from_asset
                                             , to_volume=to_volume
                                             , to_asset=to_asset
                                             , price=price
                                             , ex=flag
                                             , txn_type=txn_type
                                             , txn_href=txn_href
                                             , updated_at=msg_date
                                             )
                    else:
                        whale = WhaleEth(from_volume=from_volume
                                         , from_asset=from_asset
                                         , to_volume=to_volume
                                         , to_asset=to_asset
                                         , price=price
                                         , ex=flag
                                         , txn_type=txn_type
                                         , txn_href=txn_href
                                         , updated_at=msg_date
                                         )
                    session.add(whale)
                    session.commit()
                except Exception as err:
                    session.rollback()
                    # print('count=' + str(count))
                    print(err)
        session.close()
        print('count=' + str(count))


if __name__ == '__main__':
    print('test')
    # read_json_data("data/uni_whales.json", "uni")
    read_json_data("data/cake_whales.json", "cake")
    # read_json_data("data/sushi_whales.json", "sushi")
