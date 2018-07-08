import os
import flask_login
import sqlite3
from subscribie import current_app, request
from email.mime.text import MIMEText
from base64 import b64encode, urlsafe_b64encode
import smtplib

app = current_app

class User(flask_login.UserMixin):
    pass

def generate_login_url(email):                                                   
    con = sqlite3.connect(app.config["DB_FULL_PATH"])                            
    cur = con.cursor()                                                           
    cur.execute('SELECT COUNT(*) FROM user WHERE email=?', (email,))                
    result = bool(cur.fetchone()[0])                                             
    con.close()                                                                  
    if result is False:                                                          
        return("Invalid valid user")                                             
    # Generate login token                                                       
    login_token = urlsafe_b64encode(os.urandom(24))                              
    con = sqlite3.connect(app.config["DB_FULL_PATH"])                            
    cur = con.cursor()                                                           
    # Insert login token into db                                                    
    cur.execute(""" UPDATE user SET login_token= ? WHERE email= ? """,(login_token,email))
    con.commit()                                                                 
    con.close()                                                                  
    login_url = ''.join([request.host_url, 'login/', login_token])               
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
        s = smtplib.SMTP(app.config['EMAIL_HOST'])                               
        s.sendmail('enquiries@localhost', email, msg.as_string())     
        s.quit()                                                                 
    except Exception as e:
        print e
        return ("Failed to generate login email.")
