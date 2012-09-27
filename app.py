import os
from flask import Flask, request, url_for, render_template, flash, redirect, session
from util import *
import urllib2
import urllib
import json
from database import init_db
from models import *
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object('settings')
init_db()

CATALOG     = "http://datawarecatalog.appspot.com"
REALM       = "http://pure-lowlands-6585.herokuapp.com"
CLIENTNAME  = "herokuclient"

#catalog must provide an api for us to get these!
RESOURCEUSERNAME = "tlodgecatalog" 
RESOURCENAME     = "homework"

@app.route('/')
def root():
    session['logged_in'] = True 
    return render_template('summary.html')

@app.route('/resources')
def resources():
    return render_template('resources.html', catalogs=["http://datawarecatalog.appspot.com"], processors=getProcessorRequests());
    
@app.route('/request_resources')
def request_resources():
    catalog  =  request.args.get('catalog_uri', None)  
    client = getMyIdentifier(catalog)
    url = "%s/client_list_resources?client_id=%s&client_uri=%s" % (catalog, client.id, client.redirect) 
    f = urllib2.urlopen(url)
    data = f.read()  
    f.close()
    return data
    
    
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':
        catalog = request.form['catalog_uri']
        
        url = "%s/client_register" % catalog
        
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
            addIdentifier(catalog, "%s/%s" % (REALM, "processor"), result['client_id'])
        
        flash('Successfully regsitered with %s' % catalog)
        return redirect(url_for('resources'))
    
    else:
    
        return render_template('register.html', catalogs=["http://datawarecatalog.appspot.com"])
        

@app.route('/request', methods=['GET','POST'])
def request_processor():
    
    error = None
    
    if request.method == 'POST':
       
        expiry = request.form['expiry']
        catalog = request.form['catalog'] 
        query = request.form['query']
        resource_name = request.form['resource_name']
        owner = request.form['owner']
        state = generateuniquestate()
        client = getMyIdentifier(catalog)
    
        values = {
            'client_id': client.id,
            'state': state,
            'redirect_uri': client.redirect,
            'scope': '{"resource_name" : "%s", "expiry_time": %s, "query": "%s"}' % (resource_name,expiry,query)
        }
        
       
        app.logger.info(values)
       
        url = "%s/user/%s/client_request" % (catalog,owner)
        
        app.logger.info(url)
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url,data)
        response = urllib2.urlopen(req)
        result = response.read()
        result = json.loads( 
                result.replace( '\r\n','\n' ), 
                strict=False 
            )
            
        app.logger.info(result)    
        
        if (not(result['success'])):
            return result
        
        #"%s:%s" % (result['error_description'], result['error'])
        
        #store the state and the code and the various bits for re-use?
         
        addProcessorRequest(state=state, catalog=catalog, resource=resource_name,redirect=client.redirect,expiry=int(expiry),query=query)
        app.logger.info("returning success!")
        
        return json.dumps({'status':'success'})
    
    else:
        #provide the user with the options relating to our catalogs
        options = {
            'catalogs': [CATALOG],
            'resources': [RESOURCENAME],
            'owners': [RESOURCEUSERNAME]
        }
        return render_template('request.html', options=options, error=error)
    
@app.route('/processor')
def token():
    code  =  request.args.get('code', None)
    state =  request.args.get('state', None)
    prec = updateProcessorRequest(state=state, code=code)
    #now obtain the code!
    
    if not(prec is None): 
        url = '%s/client_access?grant_type=authorization_code&redirect_uri=%s&code=%s' % (prec.catalog, prec.redirect,code)
        
        f = urllib2.urlopen(url)
        
        data = f.read()
        
        f.close()
        
        result = json.loads(data.replace( '\r\n','\n' ), strict=False)
        
        if result["success"]:
            updateProcessorRequest(state=state, token=result["access_token"])
            
            return "Successfully obtained token <a href='%s'>return to catalog</a>" % prec.catalog
        else:
            return result
            
    return "Hmmm couldn't retrieve the token"
 
@app.route('/purge')
def purge():
    purgedata()
    return redirect(url_for('root'))

@app.route('/execute', methods=['GET','POST'])
def execute():
    if request.method == 'POST':
        print "got a post!"
        state = request.form['state']
        parameters = request.form['parameters']
        print "state=%s and params = %s" % (state, parameters)
        
        processor = getProcessorRequest(state=state)
        
        if not(processor is None):
            #NOTE THE THIRD PARTY CLIENT HAS NO IDEA OF THE URL OF THE PROCESSING ENTITY
            #SO IT NEEDS TO GET THIS SOMEHOW WITH ITS INTERACTION WITH THE CATALOG!
            url = 'http://hwresource.block49.net:9000/invoke_processor'    
    
            values = {
                'access_token':processor.token,
                'parameters': parameters
            }

            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
            response = urllib2.urlopen(req)
            data = response.read()
            
            result = json.loads(data.replace( '\r\n','\n' ), strict=False)
             
            if result['success']:
                values = result['return']
                if isinstance(values, list):
                    if len(values) > 0:
                        if isinstance(values[0], dict):
                            keys = list(values[0].keys())
                            return render_template('result.html', result=values, keys=keys)
                
                return data
                
            elif result['error_description']:
                return result['error_description'];
                
        return "Error"
    else:
        processors = getProcessorRequests()
        print processors
        return render_template('execute.html', processors=processors)
                
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
   
    app.run(debug=True,host='0.0.0.0', port=port)
