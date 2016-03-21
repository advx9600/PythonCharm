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

    def getFirstUser(self):
        return session.query(TbUser).first()

    # def startSession(self):
    #     session.begin(True)
    def commitSession(self):
        session.commit()
    def rollbackSession(self):
        session.rollback()

class TbConfig(Base):
    __tablename__ = 'tb_config'
    id = Column( Integer, primary_key=True,autoincrement=True)
    name = Column(String, unique=True, nullable=True)
    val = Column(String)

    def __repr__(self):
        return "<Config(name='%s',val='%s')>" % (self.name,self.val)

    def commitSession(self):
        session.commit()
    def rollbackSession(self):
        session.rollback()

    ### those method are auto generated
    def GetVersion(self):
        return str(session.query(TbConfig).filter_by(name='version').one().val)
    def SetVersion(self,val):
      session.query(TbConfig).filter_by(name='version').update({TbConfig.val:str(val)})
    def GetWinX(self):
      return str(session.query(TbConfig).filter_by(name='win_x').one().val)
    def SetWinX(self,val):
      session.query(TbConfig).filter_by(name='win_x').update({TbConfig.val:str(val)})
    def GetWinY(self):
      return str(session.query(TbConfig).filter_by(name='win_y').one().val)
    def SetWinY(self,val):
      session.query(TbConfig).filter_by(name='win_y').update({TbConfig.val:str(val)})
    def GetWinW(self):
      return str(session.query(TbConfig).filter_by(name='win_w').one().val)
    def SetWinW(self,val):
      session.query(TbConfig).filter_by(name='win_w').update({TbConfig.val:str(val)})
    def GetWinH(self):
      return str(session.query(TbConfig).filter_by(name='win_h').one().val)
    def SetWinH(self,val):
      session.query(TbConfig).filter_by(name='win_h').update({TbConfig.val:str(val)})
    def GetLastCallNum(self):
      return str(session.query(TbConfig).filter_by(name='last_call_num').one().val)
    def SetLastCallNum(self,val):
      session.query(TbConfig).filter_by(name='last_call_num').update({TbConfig.val:str(val)})
    def GetIsUseIce(self):
      return str(session.query(TbConfig).filter_by(name='is_use_ice').one().val)
    def SetIsUseIce(self,val):
      session.query(TbConfig).filter_by(name='is_use_ice').update({TbConfig.val:str(val)})
    def GetIsUseStun(self):
      return str(session.query(TbConfig).filter_by(name='is_use_stun').one().val)
    def SetIsUseStun(self,val):
      session.query(TbConfig).filter_by(name='is_use_stun').update({TbConfig.val:str(val)})
    def GetIsUseTurn(self):
      return str(session.query(TbConfig).filter_by(name='is_use_turn').one().val)
    def SetIsUseTurn(self,val):
      session.query(TbConfig).filter_by(name='is_use_turn').update({TbConfig.val:str(val)})
    def GetStunServer(self):
      return str(session.query(TbConfig).filter_by(name='stun_server').one().val)
    def SetStunServer(self,val):
      session.query(TbConfig).filter_by(name='stun_server').update({TbConfig.val:str(val)})
    def GetTurnServer(self):
      return str(session.query(TbConfig).filter_by(name='turn_server').one().val)
    def SetTurnServer(self,val):
      session.query(TbConfig).filter_by(name='turn_server').update({TbConfig.val:str(val)})
    def GetSipSendPort(self):
      return str(session.query(TbConfig).filter_by(name='sip_send_port').one().val)
    def SetSipSendPort(self,val):
      session.query(TbConfig).filter_by(name='sip_send_port').update({TbConfig.val:str(val)})
    def GetLogLevel(self):
      return str(session.query(TbConfig).filter_by(name='log_level').one().val)
    def SetLogLevel(self,val):
      session.query(TbConfig).filter_by(name='log_level').update({TbConfig.val:str(val)})


def InitalData():
    if (session.query(TbConfig).count() ==0):
        session.begin(True)
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
            #     getMethodImg="  return str(session.query(TbConfig).filter_by(name='"+name+"').one().val)"
            #     print getMethod
            #     print getMethodImg
            #
            #     setMethod ="def Set"+firstUpper+"(self,val):"
            #     setMethodImg= "  session.query(TbConfig).filter_by(name='"+name+"').update({TbConfig.val:str(val)})"
            #     print setMethod
            #     print setMethodImg
            TbConfig(name='version',val='1.0.0'),

            TbConfig(name='win_x',val='100'),
            TbConfig(name='win_y',val='100'),
            TbConfig(name='win_w',val='500'),
            TbConfig(name='win_h',val='420'),
            TbConfig(name='last_call_num',val=''),

            TbConfig(name='is_use_ice',val='1'),
            TbConfig(name='is_use_stun',val='1'),
            TbConfig(name='is_use_turn',val='1'),
            TbConfig(name='stun_server',val='stun.pjsip.org'),
            TbConfig(name='turn_server',val='120.24.77.212:3478'),

            TbConfig(name='sip_send_port',val='6000'),
            TbConfig(name='log_level',val='1'),
        ])
        session.commit()
    # else:
    #     # update database
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