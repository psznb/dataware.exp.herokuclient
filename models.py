from database import Base
from sqlalchemy import Column, Integer, String


class Tokens(Base):
    token   = Column(String(256), primary_key=True)
    catalog = Column(String(256))
    
    def __repr__(self):
        return "%s : %s" % (token, catalog)
   