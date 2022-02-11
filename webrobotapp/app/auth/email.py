
from flask_mail import Message
from .. import mail
from threading import Thread
from flask import render_template,current_app,url_for
from flask import current_app
from ..models import User

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    send_email('[WebRobotApp] Reset Your Password',
               sender='webrobotapp2021@gmail.com',
               recipients=[user.email],
               text_body= f'''
 Dear {user.name},
 To reset your password, visit the following link:
 {url_for('auth.reset_token', token=token, _external=True)}
 If you did not make this request then simply ignore this email and no changes will be made.
 Sincerely,
 The WebRobotApp team
 ''')
    
def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()
    
def send_email_route1_photo(route,user,photo):
    print("send email")
    send_email_secur1('[WebRobotApp] Message From Route-'+ str(route) + '.',
               sender='webrobotapp2021@gmail.com',
               recipients=[user.email],
               photo=photo,
               text_body= f'''
    Dear {user.name},
    In route {route.name} - obstacle- photo attached
    ''')
    

    
def send_email_secur(subject, sender, recipients, text_body, photo):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    with open(photo, 'rb') as fp:
        msg.attach('photo.jpg', 'image/jpg', fp.read(), 'inline', headers=[['Content-ID','<photo>']])
        
    app = current_app._get_current_object()
    
    Thread(target=send_async_email, args=(app, msg)).start()
    
def send_email_secur1(subject, sender, recipients, text_body, photo):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    with open(photo, 'rb') as fp:
        msg.attach('photo.jpg', 'image/jpg', fp.read(), 'inline', headers=[['Content-ID','<photo>']])
        
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()

def send_email_admin(subject, sender, recipients, text_body, photo):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    with open(photo, 'rb') as fp:
        msg.attach('photo.jpg', 'image/jpg', fp.read(), 'inline', headers=[['Content-ID','<photo>']])
        
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()



def send_email_admin_fault(name_fault,message_admin):
    #token = user.get_reset_token()
    print("[INFO]send email to support - add fault")
    send_email_fault('[WebRobotApp] Admin - add fault',
               sender='***********@gmail.com',
               recipients='webrobotapp2021@gmail.com',
               text_body= f'''
    Dear support team,
    Admin added a new fault-{name_fault} in a application because : { message_admin }
    ''')
    
def send_email_fault(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=[recipients])
    msg.body = text_body     
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()  
     
def send_email_admin_obstacle_photo(route,photo):
    print("send email")
    user=User.query.filter(User.id==2).first()
    print(user)
    send_email_admin('[WebRobotApp] Message From Route-'+ str(route) + '.',
               sender='webrobotapp2021@gmail.com',
               recipients=[user.email],
               photo=photo,
               text_body= f'''
    Dear Admin,
    In route {route.name} - obstacle- photo attached
    ''')
def send_email_route_photo(route,user,photo):
    #token = user.get_reset_token()
    print("send email")
    send_email_secur('[WebRobotApp] Message From Route-'+ str(route) + '.',
               sender='webrobotapp2021@gmail.com',
               recipients=[user.email],
               photo=photo,
               text_body= f'''
    Dear {user.name},
    In route {route.name} - security patrol, photo attached
    ''')
    
