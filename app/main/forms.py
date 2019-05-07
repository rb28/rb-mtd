from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired



class OAuthForm(FlaskForm):
    auth_id = StringField('Auth Id' , validators = [DataRequired()])
    submit = SubmitField('Request Authorization')


class RedirectForm(FlaskForm):
    code = StringField('Authorization Code' , validators = [DataRequired()])
    submit = SubmitField('Request Access Token')


class TokenForm(FlaskForm):
    access_token = StringField('Access Token' , validators = [DataRequired()])
    refresh_token = StringField('Refresh Token' , validators = [DataRequired()])
    expires_in = StringField('Expires In' , validators = [DataRequired()])
    scope = StringField('Scope' , validators = [DataRequired()])
    token_type = StringField('Token Type' , validators = [DataRequired()])
    submit = SubmitField('Save')


