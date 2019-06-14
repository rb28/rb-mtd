from flask import current_app
from rauth import OAuth2Service
from flask import redirect, url_for
from flask import request
import json

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
            authorize_url='https://test-api.service.hmrc.gov.uk/oauth/authorize',
            access_token_url='https://test-api.service.hmrc.gov.uk/oauth/token',
            base_url='https://test-api.service.hmrc.gov.uk/'
        )

    
    def authorize(self):
        ''' Returns a formatted authorize URL. '''
        return redirect(self.service.get_authorize_url(
            scope='read:vat+write:vat',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    
    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder= decode_json
        )
        access_token = oauth_session
        return access_token
