from database import Base, db_session
from sqlalchemy import Column, Integer, String, BigInteger

class Identifier(Base):
    __tablename__ = 'identifiers'
    id = Column(String(256), primary_key=True)
    redirect = Column(String(256))
    catalog  = Column(String(256))
    
    def __repr__(self):
        return "{id:'%s', redirect:'%s', catalog:'%s'}" % (self.id, self.redirect, self.catalog)

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
        return "{state:'%s', resource:'%s', id:'%s', expiry: %d, redirect:'%s', catalog:'%s', query:'%s', code:'%s', token:'%s'}" % (self.state, self.resource, self.id, self.expiry, self.redirect, self.catalog, self.query, self.code, self.token)
        
def addIdentifier(catalog, redirect, clientid):   
    identifier = Identifier(id=clientid, redirect=redirect, catalog=catalog)
    db_session.add(identifier)
    db_session.commit()
    print identifier
    return True
    
def addProcessorRequest(state, catalog, resource, redirect, expiry, query):   
    prorec = ProcessingRequest(state=state, catalog=catalog, resource=resource, 
                         redirect=redirect, expiry=expiry, query=query)
    db_session.add(prorec)
    db_session.commit()
    return True

def lookupProcessorRequest(state): 
    return ProcessingRequest.query.filter(ProcessingRequest.state==state).first()

def updateProcessorRequest(state, code=None, token=None):

    p = db_session.query(ProcessingRequest).filter(ProcessingRequest.state==state).first()
    
    if (not(p is None)):
        if (not(code is None)):
            p.code = code
        if (not(token is None)):
            p.token = token
        
        db_session.commit()
        return p
        
    return None

def getMyIdentifier(catalog):
    #return {'id':'something','redirect':'somewhere','catalog':'acatalog'}
    return Identifier.query.filter(Identifier.catalog==catalog).first()
