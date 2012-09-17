from database import Base, db_session
from sqlalchemy import Column, Integer, String, BigInteger

class Identifier(Base):
    __tablename__ = 'identifiers'
    id = Column(String(256), primary_key=True)
    redirect = Column(String(256))
    catalog  = Column(String(256))
    
    def __repr__(self):
        return "{id:'%s', redirect:'%s', catalog:'%s'}" % (id, redirect, catalog)

class ProcessingRequest(Base):
    __tablename__ = 'processingrequest'
    state = Column(String(256), primary_key=True)
    catalog = Column(String(256))
    resource = Column(String(256))
    redirect =  Column(String(256))
    expiry = Column(BigInteger)
    query = Column(String(512))
    code = Column(String(256))
    token = Column(String(256))
    
    def __repr__(self):
        return "{state:'%s', resource:'%s', id:'%s', expiry: %d, redirect:'%s', catalog:'%s', query:'%s', code:'%s', token:'%s'}" % (state, resource, id, expiry, redirect, catalog, query,code,token)
        
def addIdentifier(catalog, redirect, clientid):   
    identifier = Identifier(id=clientid, redirect=redirect, catalog=catalog)
    db_session.add(identifier)
    db_session.commit()
    return True
    
def addProcessorRequest(state, catalog, resource, redirect, expiry, query):   
    
    prorec = ProcessingRequest(state=state, catalog=catalog, resource=resource, 
                         redirect=redirect, expiry=expiry, query=query)
    db_session.add(prorec)
    db_session.commit()
    return True

def lookupProcessorRequest(state): 
    return Identifier.query.filter(ProcessingRequest.state==state).first()

def updateProcessorRequest(state, code):
    db_session.query.filter(ProcessingRequest.state=state).update({ProcessingRequest.code: code})
    db_session.commit()

def getMyIdentifier(catalog):
    #return {'id':'something','redirect':'somewhere','catalog':'acatalog'}
    return Identifier.query.filter(Identifier.catalog==catalog).first()
