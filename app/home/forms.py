from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import User, Organisation, Role



class UserRegisterForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name')
    lastname = StringField('First Name')
    is_admin = BooleanField('Is Admin')
    active = BooleanField('Active')
    password = PasswordField('Password', [DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired() , EqualTo('password')])
    submit=SubmitField('Register')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')


class UserAssignForm(FlaskForm):
    """
    Form for admin to assign organisation and roles to employees
    """
   
    organisation = QuerySelectField(query_factory=lambda: Organisation.query.all(),
                                  get_label="name")
    role = QuerySelectField(query_factory=lambda: Role.query.all(),
                            get_label="name")
    
    submit = SubmitField('Submit')


class OrganisationForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    code = StringField('Organisation Code', validators=[DataRequired()])
    vrn = StringField('Vat Registration Number', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RoleForm(FlaskForm):
    """
    Form for admin to add or edit a role
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    
    
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')