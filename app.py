import os
import urllib2
import urllib
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
root = "http://datawarecatalog.appspot.com"
uri  = "http://pure-lowlands-6585.herokuapp.com"
clientname = "herokuclient"

@app.route('/')
def root():
	return "hello"


@app.route('/register')
def register():
    url = "%s/client_register" % root
    values = {
                'redirect_uri':uri,
                'client_name':clientname
             }
    data = urllib.urlencode(values)
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
    app.debug = True
    app.run(port=8080, host='0.0.0.0')
