from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField, SubmitField,PasswordField, ValidationError
from wtforms.validators import DataRequired,Email,EqualTo
from ..models import Station,User,Mode,Faults,Video,Photo,StatusRoute
import phonenumbers



class UserForm(FlaskForm):
    """
    Form for admin to add or edit a user
    """
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                          EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Submit')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')
 
class UserForm_Edit(FlaskForm):
    """
    Form for admin to add or edit a user
    """
    name = StringField('name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    is_activity_user =BooleanField('Active ?', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
    

class ModeForm(FlaskForm):
    """
    Form for admin to add or edit a model
    """
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class FaultForm(FlaskForm):
    """
    Form for admin to add or edit a fault
    """
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class StationForm(FlaskForm):
    """
    Form for admin to add or edit a station
    """
    name = StringField('name', validators=[DataRequired()])
    
    submit = SubmitField('Submit')


class FaultsForm(FlaskForm):
    """
    Form for admin to add or edit a station
    """
    name = StringField('name', validators=[DataRequired()])
    
    submit = SubmitField('Submit')
    
