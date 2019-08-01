# -*- coding: utf-8 -*-
"""Create an application instance."""
import os
from app import db, create_app
from app.models import User, Role, Organisation


config_class = os.getenv('FLASK_ENV')
app = create_app(config_class)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'Organisation': Organisation}

# Create admin user to test with
#@app.before_first_request
#def create_user():
#    org = Organisation(code='100',name='SA')
#    user=User(username='admin', email='admin@example.com', password='password123', 
#        organisation_id=1, active=True, is_admin=True)
#    user.roles.append(Role(name='Admin'))
#    db.session.add(org)
#    db.session.add(user)
#    db.session.commit()