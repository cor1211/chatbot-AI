from . import db
from flask_login import UserMixin
from datetime import datetime
import pytz
# from sqlalchemy import Column, DateTime, func

# Setup VN timezone
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

class User(db.Model,UserMixin):
   id = db.Column(db.Integer,primary_key=True)
   email = db.Column(db.String(50),unique=True,nullable=False)
   password = db.Column(db.String(50),nullable=False)
   name = db.Column(db.String(50),nullable=False)
   
   chatSessions = db.relationship('ChatSession', backref='user')
   
      
   
class ChatSession(db.Model):
   __tablename__ = 'chatsession'
   id = db.Column(db.Integer,primary_key=True)
   name = db.Column(db.String(50),nullable=False)
   dateTime = db.Column(db.DateTime, default = lambda: datetime.now(tz=vn_tz)) # Lấy thời gian hiện tại khi bản ghi đc tạo
   history = db.Column(db.JSON)
   # ForeignKey User id
   user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
   
   messages = db.relationship('Message',backref='chatsession')
   

class Message(db.Model):
   __tablename__='message'
   id = db.Column(db.Integer,primary_key=True)
   request = db.Column(db.String(10000),nullable=False)
   response = db.Column(db.String(100000),nullable=False)
   # ForeignKey ChatSession id
   chatSession_id = db.Column(db.Integer,db.ForeignKey('chatsession.id'))


   

   
   
   