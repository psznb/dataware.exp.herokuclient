from database import Base, db_session
from sqlalchemy import Column, Integer, String

class Identifier(Base):
    __tablename__ = 'identifiers'
    id   = Column(String(256), primary_key=True)
    catalog = Column(String(256))
    
    def __repr__(self):
        return "%s : %s" % (token, catalog)

def addToken(clientid, catalog):   
    identifier = Identifier(id=clientid, catalog=catalog)
    db_session.add(identifier)
    db_session.commit()
