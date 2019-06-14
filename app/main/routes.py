import requests
import json
import webbrowser
from urllib.parse import urlparse, parse_qs
from flask import flash, render_template, redirect, url_for
from app.main import bp
from app.main.forms import OAuthForm, TokenForm, RedirectForm, TestForm
from app.auth.forms import LoginForm
from flask import session
from flask import request
from app.utils import OAuthSignIn





@bp.route('/index', methods=['GET','POST'])

def index():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        return redirect(url_for('auth.login')) 

    return render_template('/index.html', form=form)



@bp.route('/home')
#@login_required

def home():
    title = 'Main Home'
    return render_template('/home.html', title=title)




@bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    #if not current_user.is_anonymous():
    #    return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()



@bp.route('/callback/<provider>')
#@login_required
def oauth_callback(provider):
    #if not current_user.is_anonymous():
    #    return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    access_token = oauth.callback()
    return render_template('oauth_callback.html', title='OAuth-callback', access_token=access_token)


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
    redirectUri = 'http://localhost:5000/auth-redirect'                          #'https://www.example.com/auth-redirect'
    
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
        flash("ERROR: OAuth request unsuccessful. %d: %s" %{response.status_code, response.error_description})
        auth_id = ''
        return render_template( 'oauth_request.html', title='MTD-OAuth', form=form, auth_id=auth_id)
    

    url = response.url
    o = urlparse(url)
    q = parse_qs(o.query)
    auth_id = q['auth_id'][0]
    
    
    if form.validate_on_submit():
        auth_id = form.auth_id.data
        webbrowser.open_new_tab(url)
    
   
    return render_template('oauth_request.html', title='MTD-OAuth', form=form, auth_id=auth_id)



@bp.route('/auth-redirect', methods={'GET','POST'})
def oauth_redirect():
    
    form = RedirectForm()
    code = request.args.get('code')
    
   
    if form.validate_on_submit():
        code = form.code.data
        return redirect(url_for('main.exchange_authcode', code=code) )

    
    return render_template('oauth_redirect.html', title='Auth Code', form=form, code = code)



@bp.route('/exchange/<code>', methods=['GET','POST'])
def exchange_authcode(code):
    
    form = TokenForm()

    
    clientId = '7vHS_1WzmOZ4xESM5j7UB85lY2Ua'
    clientSecret = '7743c54a-eaee-4ff8-85da-5155b0c851c0'
    

     
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    redirectUri = 'http://localhost:5000/auth-redirect'
    access_token_url = 'https://test-api.service.hmrc.gov.uk/oauth/token'

    payload = {"grant_type": "authorization_code",
               "client_id": clientId,
               "client_secret": clientSecret, 
               "redirect_uri": redirectUri,
               "code": code
              }

    access_token_request = requests.post(access_token_url, data=payload)
    access_token = access_token_request.json()

    if access_token_request.status_code != 200:
              
            flash('{}: {} - {}'.format(access_token_request.status_code, access_token['error'], access_token['error_description']))
            access_token = ''
            return render_template('access_token.html', title='MTD-OAuth', form=form, access_token=access_token)
    #if form.validate_on_submit():
        
    #    token = form.token.data
    #    return render_template('')
    
    return render_template('access_token.html', title='MTD-OAuth', form=form, access_token=access_token)

#test org userid: 843628495777
#test org password: qfryqgVborki
# access token: 536e6181972ead3fd4dd374ac687227 | c7dcfe8c383973d4cc4d0db3b9e62af
# refresh token: 5e4b9b2772a39742205b4cc92c2bd58 | 3b439f79f132de28330b3ad9d89df44





@bp.route('/refresh/access_token', methods=['GET', 'POST'])
def refresh_token():
    
    form = TokenForm()

    #if form.validate_on_submit():

    #    return redirect('refresh_token.html', )

    clientId = '7vHS_1WzmOZ4xESM5j7UB85lY2Ua'
    clientSecret = '7743c54a-eaee-4ff8-85da-5155b0c851c0'
    refresh_token = '5e4b9b2772a39742205b4cc92c2bd58'
    refresh_token_url = 'https://test-api.service.hmrc.gov.uk/oauth/token'

    payload = {"grant_type": "refresh_token",
               "client_id": clientId,
               "client_secret": clientSecret, 
               "refresh_token": refresh_token
              }

    refresh_token_response = requests.post(refresh_token_url, data=payload)
    access_token = refresh_token_response.json()

    if refresh_token_response.status_code != 200:
        flash('{}: {} - {}'.format(refresh_token_request.status_code, access_token['error'], access_token['error_description']))
        access_token = ''
        return render_template('refresh_token.html', title='MTD-OAuth', form=form, access_token=access_token)

    return render_template('refresh_token.html', title='MTD-OAuth', form=form, access_token=access_token)

    







@bp.route('/retrieve/vat_obligations', methods=['GET','POST'])
def vat_obligations():
    base_url = 'https://test-api.service.hmrc.gov.uk'
    endpoint = '/organisations/vat/{vrn}/obligations'    

    return none









@bp.route('/retrieve/vat_liabilities', methods=['GET','POST'])
def vat_liabilities():
    base_url = 'https://test-api.service.hmrc.gov.uk'
    endpoint = '/organisations/vat/{vrn}/obligations'    

    return none








@bp.route('/retrieve/vat_payments', methods=['GET','POST'])
def vat_payments():
    base_url = 'https://test-api.service.hmrc.gov.uk'
    endpoint = '/organisations/vat/{vrn}/payments'    

    return none






@bp.route('/upload/vat_return', methods=['GET','POST'])
def upload_vat_return():
    title = 'MTD File Upload'
    return render_template('vat_upload.html', title=title)









@bp.route('/submit/vat_return', methods=['GET','POST'])
def submit_vat_return():
    enpoint = '/organisations/vat/{vrn}/returns'










@bp.route('/view/vat_return', methods=['GET','POST'])
def view_vat_return():
    enpoint = '/organisations/vat/{vrn}/returns/{periodKey}'









@bp.route('/test', methods=['GET','POST'])
def test():
    form = TestForm()
    new = 1
    url = 'http://docs.python.org/library/webbrowser.html'
    chrome_path = '"C:\Program Files (x86)\Google\Chrome\Application\Chrome.exe" %s'
    if form.validate_on_submit():
        webbrowser.get(chrome_path).open(url, new=new)

    return render_template('test.html', title='TEST', form=form)