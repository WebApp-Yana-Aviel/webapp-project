
from app import db
from flask_login import UserMixin
from datetime import datetime
from flask import current_app,jsonify
import os
from sqlalchemy_utils import PhoneNumberType
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False,unique=False,index=True)
    email = db.Column(db.String(50),unique=True, nullable=False,index=True)
    phone= db.Column(PhoneNumberType())
    password = db.Column(db.String(50),primary_key=False, unique=False,nullable=False)
    created_on = db.Column(db.DateTime(),default=datetime.utcnow,nullable=False)
    last_login = db.Column(db.DateTime(),default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
    is_admin=db.Column(db.Boolean,default=False,nullable=False)
    is_activity_user=db.Column(db.Boolean,default=True,nullable=False)
    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )


    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '< User: {}:{}:{}:{}>'.format(self.id,self.name,self.phone,self.email)
    #Reset Password Support in User Model
    """
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    """
        
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
         s = Serializer(current_app.config['SECRET_KEY'])
         try:
            user_id = s.loads(token)['user_id']
         except:
            return None
         return User.query.get(user_id)


class Mode(db.Model):
    """Mode account model."""

    __tablename__ = 'modes'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False,unique=True)
    def __repr__(self): 
       return '<Mode: {}>'.format(self.name)

    
class LogUser(db.Model):
     """Log User account model."""

     __tablename__ = 'loguser'
     id = db.Column( db.Integer(),primary_key=True)
     date_action=db.Column(db.DateTime(),default=datetime.utcnow)
     log_number = db.Column(db.String(20), default=datetime.now().strftime("%d.%m.%Y.%H:%M:%S"))
     fault_id=db.Column(db.Integer() ,db.ForeignKey('faults.id'))
     route_id=db.Column(db.Integer() ,db.ForeignKey('routes.id'))
     fault =db.relationship('Faults', backref='loguser', lazy=True)
     route =db.relationship('Route', backref='loguser',  lazy=True)

     def __repr__(self):
        return '<LogUser: {}>'.format(self.log_number)
    
class Faults(db.Model):
    """Faults account model."""

    __tablename__ = 'faults'
    id = db.Column( db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False,unique=True)

    def __repr__(self):
        return '<Faults: {}>'.format(self.name)

class Station(db.Model):
    """Station account model."""
    __tablename__ = 'station'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50), nullable=False,unique=True)
    
    def __repr__(self):
        return '<Station: {}>'.format(self.name)

class Route(db.Model):
    """Route account model."""
    __tablename__ = 'routes'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)      
    status_id=db.Column(db.Integer, db.ForeignKey('status_route.id'))
    mode_id=db.Column(db.Integer, db.ForeignKey('modes.id'))
    status=db.relationship('StatusRoute', backref='routes',lazy=True )
    mode =db.relationship('Mode', backref='routes',lazy=True )
    date_route=db.Column(db.DateTime(),default=datetime.utcnow,nullable=False)
    date_update = db.Column(db.DateTime(),default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
    date_start=db.Column(db.DateTime(),default=datetime.utcnow,onupdate=datetime.utcnow,nullable=True)
    def __repr__(self):
        return '<Route {}:{}>'.format(self.id,self.name)
       

class RouteUser(db.Model):
    __tablename__ = 'route_users'
    id =db.Column(db.Integer(),primary_key=True, autoincrement=True )
    route_id=db.Column(db.Integer, db.ForeignKey('routes.id'))
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'))
    user=db.relationship('User', backref='route_users',lazy=True )
    route=db.relationship('Route', backref='route_users',lazy=True )
    def __repr__(self):
        return '<RouteUser: {}:{}>'.format(self.route_id,self.user_id)
    
class Photo(db.Model):
    """Photo account model."""

    __tablename__ = 'photos'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256),unique=True)
    date_photo=db.Column(db.DateTime(),default=datetime.utcnow)
    user_id=db.Column(db.Integer() ,db.ForeignKey('users.id'))
    photo_user=db.relationship('User', backref='photos', lazy=True)
    route_id=db.Column(db.Integer, db.ForeignKey('routes.id'))
    route=db.relationship('Route', backref='photos', lazy=True)
    def __repr__(self):
        return '<Photo: {}>'.format(self.name)
class Video(db.Model):
    """Video account model."""

    __tablename__ = 'videos'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256),unique=True)
    date_video=db.Column(db.DateTime(),default=datetime.utcnow)     
    user_id=db.Column(db.Integer() ,db.ForeignKey('users.id'))
    video_user=db.relationship('User', backref='videos', lazy=True)
    routeV_id=db.Column(db.Integer ,db.ForeignKey('routes.id'))
    routeV=db.relationship('Route', backref='videos', lazy=True)

    def __repr__(self):
        return '<Video: {}>'.format(self.name)

class StatusRoute(db.Model):
    """Status account model."""

    __tablename__ = 'status_route'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),nullable=False,unique=True)
    def __repr__(self): 
       return '<StatusRoute {}:{}>'.format(self.id,self.name)
    
class RouteStation(db.Model):
    """Route status account model."""

    __tablename__ = 'route_station'
    id = db.Column(db.Integer,primary_key=True)
    route_id = db.Column(db.Integer() ,db.ForeignKey('routes.id'))
    route=db.relationship('Route', backref='route_station', lazy=True)
    station_id=db.Column(db.Integer ,db.ForeignKey('station.id'))
    station=db.relationship('Station', backref='route_station', lazy=True)
    is_Done=db.Column(db.Boolean,default=False,nullable=False)
    date_end=db.Column(db.DateTime(),nullable=True)
    is_Open=db.Column(db.Boolean,default=False,nullable=False)
    
    def __repr__(self): 
       return '<RouteStation: {}:{}>'.format(self.route_id,self.station_id)
