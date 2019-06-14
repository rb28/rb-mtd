# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
import jwt
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import Column, Model, SurrogatePK, db, reference_col, relationship, login
from app.extensions import bcrypt





user_roles = db.Table('user_roles', 
    Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True))


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    users = relationship('User', secondary=user_roles, backref='roles')
    

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)



class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    uuid = Column(db.String(36), unique=True, nullable=False)
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password_hash = Column(db.Binary(128), nullable=True)
    token = Column(db.String(32), index=True, unique=True)
    token_expiration = Column(db.DateTime)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        self.uuid = str(uuid.uuid4())
        if password:
            self.set_password(password)
        else:
            self.password_hash = None

    def set_password(self, password):
        """Set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return check_password_hash(self.password_hash, value)

    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')


    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token


    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)




    
# Set up user_loader
@login.user_loader
def load_user(id):
    return User.query.get(int(id))



class Organisation(SurrogatePK, Model):
    """docstring for ClassName"""
    __tablename__ = 'organisations'
    
    uuid = Column(db.String(36), unique=True, nullable =False )
    code = Column(db.String(3), unique=True, nullable=False)
    vrn = Column(db.String(9), unique=True)
    name = Column(db.String(50), unique=True)

    
    def __init__(self, code, **kwargs):
        self.uuid = str(uuid.uuid4())
        db.Model.__init__(self, code=code, **kwargs)
        
        


class Vat_return(SurrogatePK, Model):

    __tablename__ = 'vat_returns'

    organisation_id = reference_col('organisation')
    organisation = relationship('Organisation', backref='vat_returns')

    start = Column(db.DateTime)
    end = Column(db.DateTime)
    period_key = Column(db.String(4))
    vat_due_sales = Column(db.Numeric(10,2))
    vat_due_acquisitions = Column(db.Numeric(10,2))
    total_vat_due = Column(db.Numeric(10,2))
    vat_reclaimed_curr_period = Column(db.Numeric(10,2))
    net_vat_due = Column(db.Numeric(10,2))
    total_value_sales_ex_vat = Column(db.Numeric(10,2))
    total_value_purchases_ex_vat = Column(db.Numeric(10,2))
    total_value_goods_supplied_ex_vat = Column(db.Numeric(10,2))
    total_value_acquisitions_ex_vat = Column(db.Numeric(10,2))
    finalised = Column(db.Boolean())

    def __init__(self, code, **kwargs):
        db.Model.__init__(self, code=code, **kwargs)



class Vat_obligation(SurrogatePK, Model):

    __tablename__ = 'vat_obligations'

    organisation_id = reference_col('organisation')
    organisation = relationship('Organisation', backref='vat_obligations')

    start_date = Column(db.DateTime, nullable=False)
    end_date = Column(db.DateTime, nullable=False)
    due_date = Column(db.DateTime, nullable=False)
    status = Column(db.String(1), nullable=False)
    period_key = Column(db.String(4))
    received_date = Column(db.DateTime, nullable=True)

    def __init__(self, start_date, **kwargs):
        db.Model.__init__(self, start_date=start_date, **kwargs)



class Vat_liability(SurrogatePK, Model):

    __tablename__ = 'vat_liabilities'

    organisation_id = reference_col('organisation')
    organisation = relationship('Organisation', backref='vat_liabilities')

    period_from = Column(db.DateTime, nullable=False)
    period_to = Column(db.DateTime, nullable=False)
    charge_type = Column(db.String(3), nullable=False)
    original_amount = Column(db.Numeric(10,2), nullable=False)
    outstanding_amount = Column(db.Numeric(10,2))
    due = Column(db.DateTime)

    def __init__(self, period_from, **kwargs):
        db.Model.__init__(self, period_from=period_from, **kwargs)



