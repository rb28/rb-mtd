from flask import current_app
from rauth import OAuth2Service, OAuth2Session
from flask import redirect, url_for
from flask import request, session
import json, time
import datetime

from urllib.parse import (quote, urlencode, parse_qsl, urlsplit, urlunsplit, urljoin)

FORM_URLENCODED = 'application/x-www-form-urlencoded'
ENTITY_METHODS = ('POST', 'PUT', 'PATCH')
OPTIONAL_OAUTH_PARAMS = ('oauth_callback', 'oauth_verifier')





class OAuthSignIn(object):
    providers = None

    """docstring for ClassName"""
    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.client_id = credentials['id']
        self.client_secret = credentials['secret']
        

    def authorize(self):
        pass

    def callback(self):
        pass
    
    def get_data(self):
        pass

    def get_callback_url(self):
        return url_for('main.oauth_callback', provider=self.provider_name, 
                        _external=True)


    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]
        



class HmrcSignIn(OAuthSignIn):
    """docstring for ClassName"""
    def __init__(self):
        super(HmrcSignIn, self).__init__('hmrc')
        
        self.service = OAuth2Service(
            name='hmrc',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url='https://api.service.hmrc.gov.uk/oauth/authorize', #urljoin(self.base_url, 'oauth/authorize')
            access_token_url='https://api.service.hmrc.gov.uk/oauth/token',
            base_url='https://api.service.hmrc.gov.uk/', #urljoin(self.base_url, 'oauth/token') 
            
        )

    
    def authorize(self):
        ''' Returns a formatted authorize URL. '''
        return redirect(self.service.get_authorize_url(
            scope='read:vat+write:vat',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    
    def callback(self):
        ''' Returns access token '''
        if 'code' not in request.args:
            return None

        access_token_response = self.service.get_raw_access_token(
            data={'grant_type': 'authorization_code',
                  'code': request.args.get('code'),
                  'redirect_uri': self.get_callback_url()}
        )
        
        r = access_token_response.json()
        
        for k, v in r.items():
            if k in ("expires_in"):
                session['tokenTTL'] =  int(time.time()) + int(v)
            else:
                session[k] = v


        return session['access_token']



    def get_data(self, endpoint, params):

        self.url = urljoin('https://api.service.hmrc.gov.uk', endpoint)
        self.headers =headers = {"Accept":"application/vnd.hmrc.1.0+json",
                                 "Scope": "read:vat"}
        self.params = params

        def expired():
            if int(time.time()) > session['tokenTTL']:
                return True
            else:
                return False

        if not expired():
            access_token = session['access_token']
        else:
            refresh_token_response = self.service.get_raw_access_token(
                data={'grant_type': 'refresh_token',
                      'refresh_token': session['refresh_token']
                    }
                )

            r = refresh_token_response.json()
            for k, v in r.items():
                if k in ("expires_in"):
                    session['tokenTTL'] =  int(time.time()) + int(v)
                else:
                	session[k] = v
            

            access_token = session['access_token']

        s = OAuth2Session(client_id=self.client_id, client_secret=self.client_secret, access_token=access_token)


        response = s.request(method='GET', url=self.url, bearer_auth=True, headers=headers, params=params)

            
        return response


    def refresh_token(self):

        refresh_token_response = self.service.get_raw_access_token(
            data={'grant_type': 'refresh_token',
                  'refresh_token': session['refresh_token']
                 }
        )
        
        r = refresh_token_response.json()
        
        for k, v in r.items():
            if k in ("expires_in"):
                session['tokenTTL'] =  int(time.time()) + int(v)
            else:
                session[k] = v


        return session['refresh_token']


    def post_data(self, endpoint, data):

        self.url = urljoin('https://api.service.hmrc.gov.uk', endpoint)
        self.headers =headers = {"Accept":"application/vnd.hmrc.1.0+json",
                                 "Scope": "write:vat"}
        self.data = data


        def expired():
            if int(time.time()) > session['tokenTTL']:
                return True
            else:
                return False

        if not expired():
            access_token = session['access_token']
        else:
            refresh_token_response = self.service.get_raw_access_token(
                data={'grant_type': 'refresh_token',
                      'refresh_token': session['refresh_token']
                    }
                )

            r = refresh_token_response.json()
            for k, v in r.items():
                if k in ("expires_in"):
                    session['tokenTTL'] =  int(time.time()) + int(v)
                else:
                    session[k] = v
            

            access_token = session['access_token']

        s = OAuth2Session(client_id=self.client_id, client_secret=self.client_secret, access_token=access_token)
        response = s.request(method='POST', url=self.url, bearer_auth=True, headers=headers, data=data,)
        

        return response