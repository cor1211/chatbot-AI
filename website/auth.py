from flask import Blueprint,render_template, request, flash, redirect,url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import db


auth = Blueprint('auth',__name__)

@auth.route('/login',methods=['GET','POST'])
def login():
   if request.method =='POST':
      email = request.form.get('email')
      password = request.form.get('password')
      user = User.query.filter_by(email=email).first()
      if user:
         if check_password_hash(user.password,password):
            flash('Loged in successfully!','success')
            
            # Lưu trạng thái đăng nhập trong session
            login_user(user,remember=True)
            
            return redirect(url_for('views.homepage'))
         else:
            flash('Password incorrect','warning')
      else:
         flash('Email is invalid','warning')   
            
   return render_template('login.html', user=current_user)

@auth.route('/signup',methods=['GET','POST'])
def signup():
   if request.method == 'POST':
      name = request.form.get('name')
      email = request.form.get('email')
      password1 = request.form.get('password1')
      password2 = request.form.get('password2')
      
      if User.query.filter_by(email=email).first():
         flash('Email already exist!','warning')
      elif len(name) <2:
         flash('Name must greater than 2','warning')
      elif len(email) < 6:
         flash('Email must greater than 5','warning')
      elif len(password1) <6:
         flash('Password must greater than 5','warning')
      elif password1 != password2:
         flash('Password must be same','warning')
      else:
         new_user = User(email=email,name=name,password=generate_password_hash(password1,method='pbkdf2:sha256'))
         db.session.add(new_user)
         db.session.commit()
         flash('Create account successfuly!','success')
         
         return redirect(url_for('auth.login'))
      
   return render_template('sign_up.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('auth.login'))
   