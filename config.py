import os

basedir = os.path.abspath(os.path.dirname(__file__))



class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    OAUTH_CLIENT_ID = ''
    OAUTH_CLIENT_SECRET = ''
    MTD_API_BASE_URL = ''   

    OAUTH_CREDENTIALS = { 
            'hmrc': {'id':'ERxJkWKrU5x6PVzGOKEzgNJt51oa',          
                     'secret':'92191cbc-a12f-4d81-9bf0-9e40df915b64'
            },
            
            'server': {'token':'e8378039bd2f66d51a291df393111110'}
    }
    
''' 
    Production ClientID: ERxJkWKrU5x6PVzGOKEzgNJt51oa
               Client Secret: 92191cbc-a12f-4d81-9bf0-9e40df915b64
               Server token: e8378039bd2f66d51a291df393111110


    Development ClientID: 7vHS_1WzmOZ4xESM5j7UB85lY2Ua
                Client Secret: 7743c54a-eaee-4ff8-85da-5155b0c851c0
                Server token: a0b87dae9f4bc023a1cf921df144eb5           
'''

class Development(Config):
    """Configurations for Development."""
    
    DEBUG = True

    
    MTD_API = {
                'endpoints': {'base_url': 'https://test-api.service.hmrc.gov.uk/',
                              'obligations': '/organisations/vat/{vrn}/obligations',
                              'liabilities': '/organisations/vat/{vrn}/liabilities',
                              'payments': '/organisations/vat/{vrn}/payments',
                              'returns': '/organisations/vat/{vrn}/returns'}
    }



class Testing(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    DEBUG = True

    
class Production(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
       
    


app_config = {
    'development': Development,
    'testing': Testing,
    'production': Production
}