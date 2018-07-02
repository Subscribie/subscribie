from flask_wtf import FlaskForm                                                  
from wtforms import StringField, FloatField, FieldList, FileField, \
     validators, BooleanField, TextField
from wtforms.validators import DataRequired, Email as EmailValid
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES

class StripWhitespaceForm(FlaskForm):                                            
    class Meta:                                                                  
        def bind_field(self, form, unbound_field, options):                      
            filters = unbound_field.kwargs.get('filters', [])                    
            if unbound_field.field_class is not FieldList:                       
                filters.append(strip_whitespace)                                 
            return unbound_field.bind(form=form, filters=filters, **options)     
                                                                                 
def strip_whitespace(value):                                                     
    if value is not None and hasattr(value, 'strip'):                            
        return value.strip()                                                     
    return value 

class ItemsForm(StripWhitespaceForm):                                            
    title = FieldList(StringField('Title', [validators.DataRequired()]), min_entries=1)
    company_name = TextField('Company Name')                                     
    email = TextField('Email', [validators.Email(), validators.DataRequired()])  
    instant_payment = FieldList(BooleanField('Up-Front Payment'), min_entries=1) 
    subscription = FieldList(BooleanField('Subscription'), min_entries=1)        
    sell_price = FieldList(FloatField('Up-front Price'), min_entries=1)              
    monthly_price = FieldList(FloatField('Monthly Price'), min_entries=1)        
    selling_points = FieldList(FieldList(StringField('Unique Selling Point', [validators.DataRequired()]), min_entries=3), min_entries=1)
    images = UploadSet('images', IMAGES)                                         
    image = FieldList(FileField(validators=[FileAllowed(images, 'Images only!')]), min_entries=1)

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
