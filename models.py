from database import Base, db_session
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.dialects.postgresql import TEXT

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
    resource_uri = Column(String(256))
    redirect =  Column(String(256))
    expiry = Column(BigInteger)
    query = Column(String(512))
    code = Column(String(256))
    token = Column(String(256))
  
    def __repr__(self):
        return "{state:'%s', resource:'%s', resource_uri:'%s', expiry: %d, redirect:'%s', catalog:'%s', query:'%s', code:'%s', token:'%s'}" % (self.state, self.resource, self.resource_uri, self.expiry, self.redirect, self.catalog, self.query, self.code, self.token)

class ProcessingResponse(Base):
    __tablename__ = 'processingresponse'
    execution_id = Column(String(256), primary_key=True)
    access_token = Column(String(256))
    result = Column(TEXT)
    received = Column(Integer)
    
    def __repr__(self):
        return "{execution_id:'%s', access_token:'%s', result:'%s', received: %d}" % (self.execution_id, self.access_token, self.result, self.received)
    
def addProcessingResponse(execution_id, access_token, result, received):
    response = ProcessingResponse(execution_id = execution_id, access_token=access_token, result=result, received=received)
    db_session.add(response)
    db_session.commit()
    return True

def getProcessingResponses():
    return db_session.query(ProcessingResponse).all()
    
def addIdentifier(catalog, redirect, clientid):   
    identifier = Identifier(id=clientid, redirect=redirect, catalog=catalog)
    db_session.add(identifier)
    db_session.commit()
    print identifier
    return True
    
def addProcessorRequest(state, catalog, resource, resource_uri, redirect, expiry, query):   
    prorec = ProcessingRequest(state=state, catalog=catalog, resource=resource, resource_uri=resource_uri, redirect=redirect, expiry=expiry, query=query)
    db_session.add(prorec)
    db_session.commit()
    return True


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

def getProcessorRequest(state): 
    return db_session.query(ProcessingRequest).filter(ProcessingRequest.state==state).first()
  
def getProcessorRequests():
     return db_session.query(ProcessingRequest).all()
     
def getMyIdentifier(catalog):
    #return {'id':'something','redirect':'somewhere','catalog':'acatalog'}
    return Identifier.query.filter(Identifier.catalog==catalog).first()
    
def purgedata():
    db_session.query(ProcessingRequest).delete()
    db_session.query(Identifier).delete()
    db_session.commit()
