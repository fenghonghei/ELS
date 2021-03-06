from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 创建数据库
from dependence.config import MYSQL_PASSWORD

engine = create_engine("mysql+pymysql://root:{}@localhost:3306/test?charset=utf8".format(MYSQL_PASSWORD))
# 生成一个SqlORM 基类
Base = declarative_base()


# 定义表结构
class Latlng(Base):
    # 表名
    __tablename__ = 'latlngs'
    # 定义id,主键唯一,
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(50))
    address = Column(String(100))
    lat_lng = Column(String(50))
    create_time = Column(TIMESTAMP(True), nullable=False)


# 定义表结构
class Shop(Base):
    # 表名
    __tablename__ = 'shops'
    # 定义id,主键唯一,
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(50))
    address = Column(String(100))
    openning_hours = Column(String(50))
    phone = Column(String(50))
    flavors = Column(String(20))
    city = Column(String(20))
    latlng_id = Column(Integer, ForeignKey('latlngs.id'))
    latlng = Column(String(50))
    update_time = Column(TIMESTAMP(True), nullable=False)
    create_time = Column(TIMESTAMP(True), nullable=False, server_default=text('NOW()'))


# 定义表结构
class Food(Base):
    # 表名
    __tablename__ = 'foods'
    # 定义id,主键唯一,
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(50))
    shop_id = Column(Integer, ForeignKey('shops.id'))
    price = Column(Float)
    recent_popularity = Column(Integer)
    concept_ids = Column(String(50))
    update_time = Column(TIMESTAMP(True), nullable=False)
    create_time = Column(TIMESTAMP(True), nullable=False, server_default=text('NOW()'))


# 定义表结构
class Record(Base):
    # 表名
    __tablename__ = 'records'
    # 定义id,主键唯一,
    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer, ForeignKey('foods.id'))
    food = Column(String(50))
    price = Column(Float)
    old_popularity = Column(Integer)
    new_popularity = Column(Integer)
    concept_ids = Column(String(50))
    create_time = Column(TIMESTAMP(True), nullable=False)


class FoodConcept(Base):
    __tablename__ = 'food_concept'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    key_words = Column(String(50))


class Flavor(Base):
    __tablename__ = 'flavors'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(50))
    level = Column(Integer)
    parent_id = Column(Integer)


# 寻找Base的所有子类，按照子类的结构在数据库中生成对应的数据表信息
Base.metadata.create_all(engine)
# 创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
DBSession = sessionmaker(bind=engine, autoflush=False)
dbsession = DBSession()
dbsession.execute('alter table records convert to character set utf8;')
dbsession.execute('alter table foods convert to character set utf8;')
dbsession.execute('alter table shops convert to character set utf8;')
dbsession.execute('alter table food_concept convert to character set utf8;')
dbsession.execute('alter table latlngs convert to character set utf8;')
dbsession.execute('alter table flavors convert to character set utf8;')
