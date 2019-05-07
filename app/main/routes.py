import requests
import json
import webbrowser
from urllib.parse import urlparse, parse_qs
from flask import flash, render_template, redirect, url_for
from app.main import bp
from app.main.forms import OAuthForm, TokenForm
from flask import session


@bp.route('/index')

def home():

    return render_template('/index.html')





@bp.route('/helloworld', methods=['GET', 'POST'])
def helloworld():
    res = requests.get("https://test-api.service.hmrc.gov.uk/hello/world"
                       , headers={'Accept': 'application/vnd.hmrc.1.0+json'})
    
    if res.status_code != 200:
        raise Exception("ERROR: Api request unsuccessful.")
    data = res.json()

    return render_template( 'helloworld.html', title='RB-MTD',data=data)


   
@bp.route('/hello/application', methods=['GET','POST'])
def helloapp():
    access_token = 'a0b87dae9f4bc023a1cf921df144eb5'
    
    res = requests.get("https://test-api.service.hmrc.gov.uk/hello/application",
    	                headers={'Authorization': 'Bearer {}'.format(access_token),
    	                'Accept': 'application/vnd.hmrc.1.0+json'})

    if res.status_code != 200:
        raise Exception("ERROR: Api request unsuccessful.")
    data = res.json()

    return render_template( 'helloapp.html', title='MTDApp',data=data)



@bp.route('/request/authorization', methods=('GET','POST'))
def requestoauth():

    form = OAuthForm()
    request_url = 'https://test-api.service.hmrc.gov.uk/oauth/authorize'
    responseType = 'code'
    clientId = '7vHS_1WzmOZ4xESM5j7UB85lY2Ua'
    
    scope = 'read:vat+write:vat'
    state = 'Success'
    redirectUri = 'https://www.example.com/auth-redirect'
    
    response = requests.get(request_url,
                headers={'Accept': 'application/vnd.hmrc.1.0+json'},
                params={'response_type': responseType,
                        'scope': scope,
                        'state': state,
                        'client_id': clientId, 
                        'redirect_uri': redirectUri
                        }
                )

    if response.status_code != 200:
        flash("ERROR: OAuth request unsuccessful.")
        auth_id = ''
        return render_template( 'oauth_request.html', title='MTD-OAuth', form=form, auth_id=auth_id)

    url = response.url
    o = urlparse(url)
    q = parse_qs(o.query)
    auth_id = q['auth_id'][0]
    
    

    if form.validate_on_submit():
        auth_id = form.auth_id.data
        session['AUTH_ID'] = auth_id     
        
    
    chrome_path = 'C:/Program Files (x86)/Google/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open_new_tab(url)

    return render_template( 'oauth_request.html', title='MTD-OAuth', form=form, auth_id=auth_id)



@bp.route('/auth-redirect/<string:code>', methods={'GET','POST'})
def authredirect(code):
    
    form = RedirectForm()
    auth_id = session.get('AUTH_ID')
    auth_code = code
    
    if form.validate_on_submit():
        return redirect('/exchange', auth_code=auth_code) 

    
    return render_template('auth_redirect.html', title='Auth Code', auth_code = auth_code)



@bp.route('/exchange/<string:auth_code>', methods=['GET','POST'])
def exchange_authcode(auth_id, auth_code):
    
    form = TokenForm()
    
    clientId = '7vHS_1WzmOZ4xESM5j7UB85lY2Ua'
    clientSecret = '7743c54a-eaee-4ff8-85da-5155b0c851c0'
    authId = auth_id = session.get('AUTH_ID')
    code = auth_code

    grantType = 'authorization_code'
    headers = {'Content-Type': 'application/x-www-form-urlencoded','code': authId, 'grant_type': grantType}
    
    redirectUri = 'https://www.example.com/auth-redirect'
    access_token_url = 'https://test-api.service.hmrc.gov.uk/oauth/token'
    payload = {'grant_type': grantType
               'client_id': clientId,
               'client_secret': clientSecret, 
               'redirect_uri': redirectUri,
               'code': code
               }

    access_token_request = requests.post(access_token_url,  data=json.dumps(payload))
    access_token = access_token_request.json()

    if access_token_request.status_code != 200:
            flash('Exception: {} - {}'.format(access_token['error'], access_token['error_description']))
            access_token = ''

    if form.validate_on_submit():
        
        token = form.token.data
        return render_template('')
    
    return render_template('access_token.html', title='MTD-OAuth', form=form, access_token=access_token)

#test org userid: 843628495777
#test org password: qfryqgVborki