import os
from flask import Flask
import urllib2
import urllib

app = Flask(__name__)

CATALOG     = "http://datawarecatalog.appspot.com"
REALM       = "http://pure-lowlands-6585.herokuapp.com"
CLIENTNAME  = "herokuclient"

@app.route('/')
def root():
	return "hello"


@app.route('/register')
def register():
    url = "%s/client_register" % CATALOG
    print "url is %s" % url
    values = {
                'redirect_uri':REALM,
                'client_name':CLIENTNAME
             }
    data = urllib.urlencode(values)
    print "resuesting url... is %s" % url
    req = urllib2.Request(url,data)
    response = urllib2.urlopen(req)
    return response.read()
     
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
