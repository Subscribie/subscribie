import functools

from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, session, 
    url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from subscribie.db import get_jamla, get_db
from email.mime.text import MIMEText                                             
from base64 import b64encode, urlsafe_b64encode                                  
import smtplib
import sqlite3
import os
from forms import LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])                                            
def generate_login_token():                                                      
    form = LoginForm()                                                           
    if form.validate_on_submit():                                                
        try:                                                                     
            send_login_url(form.data['email'])                                   
            return ("Check your email")                                          
        except Exception as e:                                                   
            print e                                                              
            return ("Failed to generate login email.")

@bp.route('/login', methods=['GET'])                                             
def login():                                                                     
    jamla = get_jamla()                                                          
    form = LoginForm()                                                           
    return render_template('login.html', form=form, jamla=jamla)

@bp.route('login/<login_token>', methods=('GET', 'POST'))
def do_login(login_token):
    if len(login_token) < 10:                                                    
        return 'Invalid token'                                                   
    # Try to get email from login_token
    db = get_db()
    error = None
    user = db.execute('SELECT * FROM user WHERE login_token=?', (login_token,)
           ).fetchone()
    if user is None:
        error = 'Incorrect login token'

    if error is None:
        session.clear()
        session['user_id'] = user['email']

    # Invaldate previous token                                                   
    new_login_token = urlsafe_b64encode(os.urandom(24))                          
    db.execute('UPDATE user SET login_token=? WHERE login_token=?', (new_login_token, login_token,))
    db.commit()
                                                                                 
    email = user['email']                                                      
    return redirect(url_for('views.dashboard'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE email = ?', (user_id,)
        ).fetchone()

def generate_login_url(email):
    db = get_db()
    result = db.execute('SELECT COUNT(*) FROM user WHERE email=?', (email,)
                        ).fetchone()             
    if result is False:                                                          
        return("Invalid valid user")                                             
    # Generate login token                                                       
    login_token = urlsafe_b64encode(os.urandom(24))                              
    # Insert login token into db                                                    
    db.execute(""" UPDATE user SET login_token= ? WHERE email= ? """,(login_token,email))
    db.commit()
    login_url = ''.join([request.host_url, 'auth/login/', login_token])               
    return login_url 

def send_login_url(email):                                                       
    login_url = generate_login_url(email)                                        
    # Send email with token link                                                    
    msg = MIMEText(login_url)                                                    
    msg['Subject'] = 'Magic login'                                               
    msg['From'] = 'enquiries@localhost'                                          
    msg['To'] = email                                                            
    # Perform smtp send                                                             
    print "#"*80                                                                 
    print ''.join(["Sending Login Email to ", email, ':'])
    print login_url
    print "#"*80                                                                 
    try:                                                                         
        s = smtplib.SMTP(current_app.config['EMAIL_HOST'])                               
        s.sendmail('enquiries@localhost', email, msg.as_string())                
        s.quit()                                                                 
    except Exception as e:                                                       
        print e                                                                  
        return ("Failed to generate login email.")

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/logout')                                                             
def logout():                                                                    
    session.clear()
    return 'Logged out'
