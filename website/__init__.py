from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import google.generativeai as genai
from flask_migrate import Migrate
import markdown
import re

db = SQLAlchemy()

def create_app():
   #Create Flask App
   app = Flask(__name__)
   
   
   # Add config
   app.config['SECRET_KEY'] = '12112003'
   app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///chatbot.db'

   
   # Import and Register Blueprint
   from .auth import auth
   from .views import views
   app.register_blueprint(auth,url_prefix='/auth/')
   app.register_blueprint(views,url_prefix='/views/')
   
   #database
   db.init_app(app)
   
   migrate = Migrate(app,db)
   
   create_dtb(app)
   
   from .models import User
   
   # Login manager
   login_manager = LoginManager()
   login_manager.init_app(app)
   login_manager.login_view='auth.login'
   
   @login_manager.user_loader
   def load_user(user_id):
      return User.query.get(int(user_id))
   
   # Filer custom Jinja2
   @app.template_filter('nl2br')
   def replace_newlines(value):
      return value.replace('\n','<br>')
   
   @app.template_filter('markDstar')
   def replace_star(value):
      return markdown.markdown(value)
   
   @app.template_filter('bold_text')
   def bold_text(value):
    # Sử dụng regex để thay thế **text** bằng <strong>text</strong>
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
   
   return app

   
      

def create_dtb(app):
   if not path.exists('website/chatbot.db'):
      with app.app_context():
         db.create_all()
      print('Created dtb')

