from database import Base, db_session
from sqlalchemy import Column, Integer, String

class Identifier(Base):
    __tablename__ = 'identifiers'
    id   = Column(String(256), primary_key=True)
    catalog = Column(String(256))
    
    def __repr__(self):
        return "%s : %s" % (token, catalog)

def addToken(clientid, catalog):
    print "adding id %s %s" % (clientid, catalog)
    identifier = Identifier(id=clientid, catalog=catalog)
    print "successfully created identifier"
    db_session.add(identifier)
    print "successfully added identifier"
    db_session.commit()
    print "successfully committed!"