import os
from flask import Flask, request, url_for, render_template, flash, redirect, session
from util import *
import urllib2
import urllib
import json
import OpenIDManager
import hashlib
from database import init_db
from models import *
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config.from_object('settings')
init_db()

CATALOG     = "http://datawarecatalog.appspot.com"
REALM       = "http://pure-lowlands-6585.herokuapp.com"
CLIENTNAME  = "herokuclient"

#catalog must provide an api for us to get these!
RESOURCEUSERNAME = "tlodgecatalog" 
RESOURCENAME     = "homework"
EXTENSION_COOKIE = "tpc_logged_in"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (session.get("logged_in") == None):
            return redirect(url_for('root'))
        return f(*args, **kwargs)
    return decorated_function
    
@app.route('/')
def root():

    return render_template('login.html')
    #session['logged_in'] = True 
    #return render_template('summary.html')

@app.route('/login')
def login():

    provider = request.args.get('provider', None)  
    params=""
    
    try:
        url = OpenIDManager.process(
            realm=REALM,
            return_to=REALM + "/checkauth?" + urllib.quote( params ),
            provider=provider
        )
    except Exception, e:
        app.logger.error( e )
        return user_error( e )
    
    #Here we do a javascript redirect. A 302 redirect won't work
    #if the calling page is within a frame (due to the requirements
    #of some openid providers who forbid frame embedding), and the 
    #template engine does some odd url encoding that causes problems.
    app.logger.info("calling url %s" % url)
    
    return "<script>self.parent.location = '%s'</script>" % url

@app.route( "/checkauth")
def user_openid_authenticate():
    
    #o = OpenIDManager.Response( request.GET )
    o = OpenIDManager.Response(request.args)
  
  
    #check to see if the user logged in succesfully
    if ( o.is_success() ):
        
        user_id = o.get_user_id()
        email = o.get_user_email()
       
        #if so check we received a viable claimed_id
        if user_id:
            try:
                
                print "wohoo!  got a new user id %s emial: %s" % (user_id, email)
                session['logged_in'] = True 
                #user = db.user_fetch_by_id( user_id )
                 
                #if this is a new user add them
                #if ( not user ):
                #    db.user_insert( o.get_user_id() )
                #    user_name = None
                #else :
                #    user_name = user.user_name
                
                #_set_authentication_cookie( user_id, user_name  )
                
            except Exception, e:
                return user_error( e )
            
            
        #if they don't something has gone horribly wrong, so mop up
        else:
            _delete_authentication_cookie()

    #else make sure the user is still logged out
    else:
        _delete_authentication_cookie()
        
    try:
        # redirect_uri = "resource_request?resource_id=%s&redirect_uri=%s&state=%s" % \
        #     ( request.GET[ "resource_id" ], 
        #       request.GET[ "redirect_uri" ], 
        #       request.GET[ "state" ] )
        redirect_uri = "resources" 
    except:
        redirect_uri = REALM + ROOT_PAGE
    
    return "<script>self.parent.location = '%s'</script>" % ( redirect_uri, )
   
@app.route('/resources')
@login_required
def resources():
    return render_template('resources.html', catalogs=["http://datawarecatalog.appspot.com"], processors=getProcessorRequests());
    
@app.route('/request_resources')
@login_required
def request_resources():
    catalog  =  request.args.get('catalog_uri', None)  
    client = getMyIdentifier(catalog)
    url = "%s/client_list_resources?client_id=%s&client_uri=%s" % (catalog, client.id, client.redirect) 
    f = urllib2.urlopen(url)
    data = f.read()  
    f.close()
    print data
    return data
    
    
@app.route('/register', methods=['GET','POST'])
@login_required
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
@login_required
def request_processor():
    
    error = None
    
    if request.method == 'POST':
       
        expiry = request.form['expiry']
        catalog = request.form['catalog'] 
        query = request.form['query']
        resource_name = request.form['resource_name']
        resource_uri = request.form['resource_uri']
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
            return json.dumps({'success':False})
        
        #store the state and the code and the various bits for re-use?
         
        addProcessorRequest(state=state, catalog=catalog, resource=resource_name,resource_uri=resource_uri,redirect=client.redirect,expiry=int(expiry),query=query)
        
        return json.dumps({'success':True, 'state':state})
    
    else:
        #provide the user with the options relating to our catalogs
        options = {
            'catalogs': [CATALOG],
            'resources': [RESOURCENAME],
            'owners': [RESOURCEUSERNAME]
        }
        return render_template('request.html', options=options, error=error)
    
@app.route('/processor')
@login_required
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
@login_required
def purge():
    purgedata()
    return redirect(url_for('root'))

@app.route('/result/<execution_id>', methods=['POST'])
def result(execution_id):
    
    success = request.form['success']
    result = request.form['return']
   
    execution_request = getExecutionRequest(execution_id)
    
    if not(execution_request is None):
        addExecutionResponse(execution_id=execution_id, access_token=execution_request.access_token, result=json.dumps(result), received=int(time.time()))
        print success
        print result
    
    #if 'success' in result:
                
    #    values = result['return']
        
        #save details to allow the resource (entity we received results from) to view
        
    #    addExecutionResponse(execution_id=execution_id, access_token=processor.token, #result=json.dumps(values), received=int(time.time()))
        
    #    if isinstance(values, list):
    #        if len(values) > 0:
    #            if isinstance(values[0], dict):
    #                keys = list(values[0].keys())
    #                return render_template('result.html', result=values, keys=keys)
    #    
    #    return data
    #            
    #elif 'error_description' in result:
    #    
    #    return result['error_description']
    #    return "Error"
     
    #else:
    #    processors = getProcessorRequests()
    #    return render_template('execute.html', processors=processors)
        
    return "thanks!!"
    
@app.route('/view/<execution_id>', methods=['POST'])
def view(execution_id):
    
    #should the hwresource owner have to register with the TPC?  Think it'd be a 
    #bit of an interaction headache, better that the shared id's is assumed enough
    #to authenticate a request to view a processing output.
    
    #third party client received when this registered with catalog
    #client_id = request.form['client_id'] 
    
    #processor access token
    processor_id = request.form['processor_id'] 
    
    #lookup the execution details and confirm that this user is allowed access. Return a page
    #with the same view of the data as seen by this TPC.
    #data = getExecutionResponse(execution_id=execution_id, access_token=processor_id)
    
    values = json.loads(data.result.replace( '\r\n','\n' ), strict=False)
   
    #generalise this..
    if isinstance(values, list):
        if len(values) > 0:
            if isinstance(values[0], dict):
               keys = list(values[0].keys())
                return render_template('result.html', result=values, keys=keys)
    
    return str(data)
    

@app.route('/executions')
@login_required
def executions():
     executions = getAllExecutionResponses()
     print executions
     return render_template("executions_summary.html", executions=executions)

    
@app.route('/execute', methods=['GET','POST'])
@login_required
def execute():
    if request.method == 'POST':
    
        state = request.form['state']
        parameters = request.form['parameters'] 
        processor = getProcessorRequest(state=state)
        
        if not(processor is None):
           
            url = '%s/invoke_processor' % processor.resource_uri
            
            m = hashlib.md5()
            m.update('%f' % time.time())
            id = m.hexdigest()
                
            values = {
                'access_token':processor.token,
                'parameters': parameters,
                'result_url' : "%s/result/%s" % (REALM,id)
            }

            data = urllib.urlencode(values)
            req = urllib2.Request(url,data)
            response = urllib2.urlopen(req)
            data = response.read()
            
            result = json.loads(data.replace( '\r\n','\n' ), strict=False)
            
            addExecutionRequest(execution_id=id, access_token=processor.token, parameters=parameters, sent=int(time.time()))
            return redirect(url_for('executions'))
    else:
        processors = getProcessorRequests()
        return render_template('execute.html', processors=processors)
        
def _delete_authentication_cookie():
    
    response.delete_cookie( 
        key=EXTENSION_COOKIE,
    )
        
        
def user_error( e ):
    
    return  "An error has occurred: %s" % ( e )
            
            
               
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.ccl
    port = int(os.environ.get('PORT', 5000))
   
    app.run(debug=True,host='0.0.0.0', port=port)
 