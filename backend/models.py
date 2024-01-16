from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from sqlalchemy import func
from sqlalchemy import Time

import pytz


db = SQLAlchemy()

IST = pytz.timezone('Asia/Kolkata')

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))
    

class User(db.Model, UserMixin):
    __tablename__='user'
    id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    email=db.Column(db.String, unique=True)
    username=db.Column(db.String)
    password=db.Column(db.String(255))
    active=db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)

class Role(db.Model, RoleMixin):
    __tablename__='role'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class theater(db.Model):
    __tablename__='theater'
    theater_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    ut_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theater_name=db.Column(db.String, unique=True)
    theater_address=db.Column(db.String)
    theater_capacity=db.Column(db.Integer)
    theater_pic = db.Column(db.BLOB, nullable=False)
    theater_show=db.relationship("show", secondary="show_theater", backref="show_theater" ,cascade="all, delete")

class show(db.Model):
    __tablename__='show'
    show_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    ts_id = db.Column(db.Integer, db.ForeignKey('theater.theater_id'), nullable=False)
    show_name=db.Column(db.String)
    show_timing=db.Column(db.DateTime, nullable=False)
    show_description=db.Column(db.String)
    show_pic = db.Column(db.BLOB, nullable=False)
    show_rating = db.Column(db.Float,default=0)
    show_price=db.Column(db.Integer)
    show_duration = db.Column(db.Integer)
    show_trailer = db.Column(db.String,nullable=True)
    bookings = db.relationship("bookings", backref="show", cascade="all, delete")
    ratings = db.relationship("ShowRating", backref="show", cascade="all, delete")

    
class bookings(db.Model):
    __tablename__='booking'
    booking_id=db.Column(db.Integer, autoincrement=True, primary_key=True)
    booking_tickets_count =db.Column(db.Integer, nullable=False)
    booking_time=db.Column(db.DateTime, nullable=False, default=datetime.now(IST))
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    show_id=db.Column(db.Integer, db.ForeignKey("show.show_id"), nullable=False)
    seat_range = db.Column(db.String, nullable=False)
    
class ShowTheater(db.Model):
    __tablename__ = 'show_theater'
    show_theater_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey("show.show_id"), nullable=False)
    theater_id = db.Column(db.Integer, db.ForeignKey("theater.theater_id"), nullable=False)
    total_bookings = db.Column(db.Integer,nullable = True,default=0)  
    available_tickets = db.Column(db.Integer, nullable=True)

class ShowRating(db.Model):
    __tablename__ = 'show_rating'
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.show_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_rating = db.Column(db.Integer, nullable=False)

class ShowTags(db.Model):
    __tablename__ = 'show_tags'
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.show_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_tag = db.Column(db.Integer, nullable=False)
   
class PopularityPrediction(db.Model):
    __tablename__ = 'popularity_prediction'
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.show_id'), nullable=False)
    predicted_booking_count = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(IST))