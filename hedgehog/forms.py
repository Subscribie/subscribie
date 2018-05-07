from flask_wtf import FlaskForm                                                  
from wtforms import StringField, FloatField, FieldList, FileField, \
     validators, BooleanField, TextField
from wtforms.validators import DataRequired, Email as EmailValid

class LoginForm(FlaskForm):                                                      
    email = StringField('email', validators= [ DataRequired(), EmailValid()])    
                                                                                 
class CustomerForm(FlaskForm):                                                   
    given_name = StringField('given_name', validators = [DataRequired()])        
    family_name = StringField('family_name', validators = [DataRequired()])      
    mobile = StringField('mobile', validators = [DataRequired()])                
    email = StringField('email', validators = [DataRequired()])                  
    address_line_one = StringField('address_line_one', validators = [DataRequired()])
    city = StringField('city', validators = [DataRequired()])                    
    postcode = StringField('postcode', validators = [DataRequired()])            
                                                                                 
class GocardlessConnectForm(FlaskForm):                                          
    access_token = StringField('access_token', validators = [DataRequired()])    
                                                                                 
class StripeConnectForm(FlaskForm):                                              
    publishable_key = StringField('publishable_key', validators = [DataRequired()])
    secret_key = StringField('secret_key', validators = [DataRequired()]) 
