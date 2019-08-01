# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
import jwt
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import Column, Model, SurrogatePK, db, reference_col, relationship, login, TimestampMixin
from app.extensions import bcrypt



user_roles = db.Table('user_roles', 
    Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True))



class Organisation(SurrogatePK, Model):
    """docstring for ClassName"""
    __tablename__ = 'organisations'
    
    uuid = Column(db.String(36), unique=True, nullable =False )
    code = Column(db.String(3), unique=True, nullable=False)
    vrn = Column(db.String(9), unique=True)
    name = Column(db.String(50), unique=True)

    # Relationships
    users = relationship('User', backref='organisation')
    vat_returns = relationship('Vat_return', backref='organisation')

    
    def __init__(self, code, **kwargs):
        self.uuid = str(uuid.uuid4())
        db.Model.__init__(self, code=code, **kwargs)
        
    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Organisation({name})>'.format(name=self.name)   



class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    description = Column(db.String(160), nullable=True)
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
    email = Column(db.String(80), unique=False, nullable=False)
    organisation_id = reference_col('organisations', nullable=True,)
    #role_id = reference_col('roles', nullable=True,)
    #: The hashed password
    password_hash = Column(db.String(128), nullable=True)
    token = Column(db.String(32), index=True, unique=True, nullable=True)
    token_expiration = Column(db.DateTime, nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=True,  nullable=True)
    is_admin = Column(db.Boolean(), default=False, nullable=True)

    def __init__(self, username, email, active,  password=None,  **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, active=active, **kwargs)
        self.uuid = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.active = active
        
       
        if password:
            self.set_password(password)
        else:
            self.password_hash = None

    
    
    def has_admin(self):
        """Admin or non admin user (required by flask-login)"""
        return self.is_admin

    
    def is_active(self):
        """Active or non active user (required by flask-login)"""
        return self.active


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



class Vat_return(SurrogatePK, Model, TimestampMixin):

    __tablename__ = 'vat_returns'

    organisation_id = reference_col('organisations', nullable=False)
    
    period_key = Column(db.String(4))
    vat_due_sales = Column(db.String(10))
    vat_due_acquisitions = Column(db.String(10))
    total_vat_due = Column(db.String(10))
    vat_reclaimed_curr_period = Column(db.String(10))
    net_vat_due = Column(db.String(10))
    total_value_sales_ex_vat = Column(db.String(10))
    total_value_purchases_ex_vat = Column(db.String(10))
    total_value_goods_supplied_ex_vat = Column(db.String(10))
    total_acquisitions_ex_vat = Column(db.String(10))
    finalised = Column(db.Boolean(), default=True)
    is_submitted = Column(db.Boolean(), default=False)
    submitted_on = Column(db.DateTime, nullable = True)
    submitted_by = Column(db.String(50), nullable=True)

    def __init__(self, organisation_id, period_key, **kwargs):
        db.Model.__init__(self, organisation_id=organisation_id, period_key=period_key, **kwargs)


    def is_submitted(self):
        """Active or non active user (required by flask-login)"""
        return self.is_submitted


class Vat_receipt(SurrogatePK, Model):
    __tablename__ = 'vat_receipts'

    organisation_id = reference_col('organisations', nullable=False)
    period_key = Column(db.String(4))
    processing_date = Column(db.DateTime, nullable = True)
    payment_indicator = Column(db.String(10))
    form_bundle_number = Column(db.String(12))
    charge_ref_number = Column(db.String(12))


    def __init__(self, organisation_id, period_key, processing_date, **kwargs):
        db.Model.__init__(self, organisation_id=organisation_id, period_key=period_key, processing_date=processing_date, **kwargs)
        
