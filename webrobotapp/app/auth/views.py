from flask import Blueprint, redirect, render_template, flash, request, session, url_for
from flask_login import login_required, logout_user, current_user, login_user
from . import auth
from .forms import LoginForm, RegistrationForm,ResetResetForm,ResetPasswordForm
from .. import db
from ..models import User,LogUser,RouteUser,RouteStation,Route
from .email import  send_reset_email
from twilio.rest import Client 
from time import sleep
import json
import datetime

conf_path='/home/webrgacv/webrobotapp/app/home/conf/twilio.json'

@auth.route('/login', methods=['GET', 'POST'])
def login():
        form = LoginForm()
      
        # Validate login attempt
        if form.validate_on_submit():
             user = User.query.filter_by(email=form.email.data).first()  
             if user is not None and user.is_activity_user==0:
                 flash('Inactive user, please contact admin ')
             elif user is not None and user.check_password(password=form.password.data):
                 login_user(user,remember=form.remember.data)
                 if user.is_admin:
                     return redirect(url_for('home.admin_dashboard'))
                 flash('You have successfully been logged in')
                 # redirect to the dashboard page after login
                 send_sms_message()
                 return redirect(url_for('home.profile'))
             else:
                 flash('Invalid username/password combination')
             
        return render_template('auth/login.html', form=form, title='Login')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    
             form = RegistrationForm()
             if form.validate_on_submit():
                user = User(name=form.name.data,email=form.email.data,phone=form.phone.data)
                user.set_password(form.password.data)

                # add employee to the database
                db.session.add(user)
                db.session.commit()
                flash('You have successfully registered! You may now login.')
                login_user(user) 
                # redirect to the login page
                return redirect(url_for('auth.login'))

             # load registration template
             return render_template('auth/register.html', form=form, title='Register')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully been logged out.')
    return redirect(url_for('home.index'))


# Reset Password Request Route
@auth.route('/reset_password', methods = ['GET', 'POST'])
def reset_request():

    if current_user.is_authenticated:
        return redirect(url_for('home.profile'))

    form = ResetResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_reset_email(user)
            flash("Please check your email for the instructions to reset your password")
            return redirect(url_for('auth.login'))

    return render_template('/auth/reset_request.html', title = "Request For Reset Password", form = form)

# Password Reset Route
@auth.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.profile'))

    user = User.verify_reset_token(token)

    if not user:
        flash("Invalid Token")
        return redirect(url_for('auth.reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.add(user)  
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_token.html', title = "Reset Password", form = form) 


def send_sms_message():

    # check to see if the Twilio should be used
    f=open(conf_path)
    data=json.load(f)
    if data["use_twilio"]:    
       client = Client(data["account_sid"],data["auth_token"]) 

       message = client.messages.create( 
                              from_='+972526987310',  
                              body=current_user.name+' welcome to WebRobotApp',     
                              to=current_user.phone 
                          ) 
       print(message.sid)
    f.close()

     
