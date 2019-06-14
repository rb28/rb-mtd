import os

basedir = os.path.abspath(os.path.dirname(__file__))



class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ADMINS = ['roger.bovell@gmail.com']

    OAUTH_CREDENTIALS = { 
            'hmrc': {'id':'7vHS_1WzmOZ4xESM5j7UB85lY2Ua',
                     'secret':'7743c54a-eaee-4ff8-85da-5155b0c851c0'
            },
            
            'server': {'token':'a0b87dae9f4bc023a1cf921df144eb5'}
    }
    

class Development(Config):
    """Configurations for Development."""
    
    DEBUG = True

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