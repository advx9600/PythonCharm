__author__ = 'Administrator'

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db_1.db', echo=False)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class TbUser(Base):
    __tablename__ = 'tb_users'
    id = Column( Integer, primary_key=True,autoincrement=True)
    name = Column(String)
    pwd = Column(String)
    domain=Column(String)

    def __repr__(self):
        return "<User(name='%s',pwd='%s',domain='%s')>" % (self.name,self.pwd,self.domain)

    def getCount(self):
        return session.query(TbUser.id).count()

    def addUser(self,user):
        session.add(user)
        session.commit()

    def getFirstUser(self):
        return session.query(TbUser).first()

class TbConfig(Base):
    __tablename__ = 'tb_config'
    id = Column( Integer, primary_key=True,autoincrement=True)
    name = Column(String, unique=True, nullable=True)
    val = Column(String)

    def __repr__(self):
        return "<Config(name='%s',val='%s')>" % (self.name,self.val)

    def sessionCommit(self):
        session.commit()

    ### those method are auto generated
    def GetWinX(self):
      return session.query(TbConfig).filter_by(name='win_x').one().val
    def SetWinX(self,val):
      session.query(TbConfig).filter_by(name='win_x').update({TbConfig.val:str(val)})
    def GetWinY(self):
      return session.query(TbConfig).filter_by(name='win_y').one().val
    def SetWinY(self,val):
      session.query(TbConfig).filter_by(name='win_y').update({TbConfig.val:str(val)})
    def GetWinH(self):
      return session.query(TbConfig).filter_by(name='win_h').one().val
    def SetWinH(self,val):
      session.query(TbConfig).filter_by(name='win_h').update({TbConfig.val:str(val)})
    def GetWinW(self):
      return session.query(TbConfig).filter_by(name='win_w').one().val
    def SetWinW(self,val):
      session.query(TbConfig).filter_by(name='win_w').update({TbConfig.val:str(val)})
    def GetLastCallNum(self):
      return session.query(TbConfig).filter_by(name='last_call_num').one().val
    def SetLastCallNum(self,val):
      session.query(TbConfig).filter_by(name='last_call_num').update({TbConfig.val:str(val)})

def InitalData():
    if (session.query(TbConfig).count() ==0):
        session.add_all([
            #### from this use script auto genneric TbConfig's get and set method,like below

            # def TbConfig(name,val):
            #     # get="Get"+name.split("_")
            #     splits=name.split("_")
            #     firstUpper=""
            #     for split in splits:
            #         firstUpper += split.capitalize()
            #
            #     getMethod="def Get"+firstUpper+"(self):"
            #     getMethodImg="  return session.query(TbConfig).filter_by(name='"+name+"').one().val"
            #     print getMethod
            #     print getMethodImg
            #
            #     setMethod ="def Set"+firstUpper+"(self,val):"
            #     setMethodImg= "  session.query(TbConfig).filter_by(name='"+name+"').update({TbConfig.val:str(val)})"
            #     print setMethod
            #     print setMethodImg

            TbConfig(name='win_x',val='100'),
            TbConfig(name='win_y',val='100'),
            TbConfig(name='win_w',val='500'),
            TbConfig(name='win_h',val='420'),
            TbConfig(name='last_call_num',val=''),
        ])
        session.commit()

Base.metadata.create_all(engine)
InitalData()
# class DB():
#     session=None
#     def __init__(self):
#         Base.metadata.create_all(engine)
#         Session = sessionmaker(bind=engine)
#         self.session = Session()
#         # user = User(name="111",pwd="222")
#         # session.add(user)
#         # session.commit()