import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader                                                       
def user_loader(email):                                                          
    con = sqlite3.connect(app.config["DB_FULL_PATH"])                            
    con.row_factory = sqlite3.Row # Dict based result set                        
    cur = con.cursor()                                                           
    cur.execute('SELECT email FROM user WHERE email=?', (str(email),))           
    result = cur.fetchone()                                                      
    con.close()                                                                  
    if result is None:                                                           
        return                                                                   
    user = User()                                                                
    user.id = email                                                              
    return user

@login_manager.request_loader                                                    
def request_loader(request):                                                     
    email = request.form.get('email')                                            
    if email not in users:                                                       
        return                                                                   
    user = User()                                                                
    user.id = email                                                              
                                                                                 
    user.is_authenticated = request.form['password'] == users['email']['password']
    return user
