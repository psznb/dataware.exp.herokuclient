import os
from flask import Flask, request
from util import *
import urllib2
import urllib
import json
from database import init_db
from models import *
from datetime import datetime, timedelta

app = Flask(__name__)
init_db()

CATALOG     = "http://datawarecatalog.appspot.com"
REALM       = "http://pure-lowlands-6585.herokuapp.com"
CLIENTNAME  = "herokuclient"

#catalog must provide an api for us to get these!
RESOURCEUSERNAME = "tlodgecatalog" 
RESOURCENAME     = "homework"

@app.route('/')
def root():
	return "hello"


@app.route('/register')
def register():
    url = "%s/client_register" % CATALOG
    values = {
                'redirect_uri': "%s/%s" % (REALM, "processor"),
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
            
    if (result['success']):
        addIdentifier(CATALOG, result['client_id'])
    
    print "%s" % result['success']
    print "%s" % result['client_id']
    return "nice!!"

@app.route('/request', methods=['GET','POST'])
def request():
    
    error = None
    
    if request.method == 'POST':
       
        expiry = request.form['expiry']
        query = request.form['query']
        resource = request.form['resource']
        state = generaterandomstate()
        client_id = getIdentifier(CATALOG)
       
        values = {
            'client_id': client_id,
            'state': state,
            'redirect_uri': "%s/%s" % (REALM, "processor"),
            'scope': '{"resource_name" : "%s", "expiry_time": %s, "query": "%s"}' % (resource,expiry,query)
        }
        url = "%s/client_request" % CATALOG
        data = urllib.urlencode(values)
        req = urllib2.Request(url,data)
        response = urllib2.urlopen(req)
        result = response.read()
        result = json.loads( 
                result.replace( '\r\n','\n' ), 
                strict=False 
            )
            
        return "done it" 
    else:
       return render_template('request.html', error=error)
    
@app.route('/processor')
def token():
    code  =  request.args.get('code', None)
    state =  request.args.get('state', None)
    return "thanks!"
    
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
