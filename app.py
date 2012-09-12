import os
from flask import Flask
import urllib2
import urllib
import json
from database import init_db

app = Flask(__name__)
init_db()

CATALOG     = "http://datawarecatalog.appspot.com"
REALM       = "http://pure-lowlands-6585.herokuapp.com"
CLIENTNAME  = "herokuclient"

@app.route('/')
def root():
	return "hello"


@app.route('/register')
def register():
    url = "%s/client_register" % CATALOG
    values = {
                'redirect_uri':REALM,
                'client_name':CLIENTNAME
             }
    
    data = urllib.urlencode(values)
    req = urllib2.Request(url,data)
    response = urllib2.urlopen(req)
    result = response.read()
    result = json.loads( 
                result.replace( '\r\n','\n' ), 
                strict=False 
            )        
    print "%s" % result['success']
    print "%s" % result['client_id']
    return "nice!!"
    
@app.route('/invoke')
def invoke():

    url = 'http://128.243.22.219/invoke_processor'    
    
    values = {
                'access_token':'pPMVHkZWe5fqedk*KENG1liiBcs8iiTyC4H5YLC1XcE=',
                'parameters':'{}'
              }

    data = urllib.urlencode(values)
    req = urllib2.Request(url,data)
    response = urllib2.urlopen(req)
    return response.read()

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True,host='0.0.0.0', port=port)
