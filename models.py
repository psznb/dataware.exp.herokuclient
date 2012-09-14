from database import Base, db_session
from sqlalchemy import Column, Integer, String

class Identifier(Base):
    __tablename__ = 'identifiers'
    id = Column(String(256), primary_key=True)
    redirect = Column(String(256))
    catalog  = Column(String(256))
    
    def __repr__(self):
        return "{id:%s, redirect:%s, catalog:%s}" % (id, redirect, catalog)

def addIdentifier(catalog, redirect, clientid):   
    identifier = Identifier(id=clientid, redirect=redirect, catalog=catalog)
    db_session.add(identifier)
    db_session.commit()
    return True
    
def getMyIdentifier(catalog):
    #return {'id':'something','redirect':'somewhere','catalog':'acatalog'}
    return Identifier.query.filter(Identifier.catalog==catalog).first()
