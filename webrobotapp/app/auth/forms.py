# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError,BooleanField
from wtforms.validators import DataRequired, Email, EqualTo,Length, ValidationError

from ..models import User
import phonenumbers


class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Username', validators=[DataRequired()])
    phone =StringField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
                
class LoginForm(FlaskForm):
    """
    Form for users to login
    """
    email = StringField('Email',validators=[DataRequired(),Email(message='Enter a valid email.')] )
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField("Remember", default=False) 
    submit = SubmitField('Log In')

# Reset Password Request Form
class ResetResetForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(message = "Email Address is required."), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. You must register first.")

#Password Reset Form
class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators = [DataRequired(message = "Password is required.")], render_kw = {"placeholder": "Password"})
    confirm_password = PasswordField("Repeat Password", validators = [DataRequired(message = "Password Confirmation is required."), EqualTo("password")], render_kw = {"placeholder": "Confirm Password"})
    submit = SubmitField("Reset Password")

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    passwordNew = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(
                min=6,
                max=40,
                message='Password must be within 6 and 40 characters')])
    confirm_password = PasswordField(
        'Confirm New Password', validators=[
            DataRequired(), EqualTo('passwordNew')])
    submit = SubmitField('Change Password')

class ConfirmPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ConfirmPasswordConfirm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = BooleanField('I confirm', validators=[DataRequired()])
    submit = SubmitField('Submit')
