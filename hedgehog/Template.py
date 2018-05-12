from .jamla import Jamla
import jinja2
import os


def load_template(app):
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])

    try:
        if os.path.isdir(jamla['template']['name']):
            #Allow template path to be specified as absolute path
            templatepath = jamla['template']['name']
        else:
            #Most client code will pass template by name
            templatepath = ''.join([app.config['TEMPLATE_FOLDER'], 
                                  jamla['template']['name'], '/'])
        if os.path.exists(templatepath) is False:
            raise
    except Exception as e:
        print "Falling back to default template"
        templatepath = ''.join([app.config['TEMPLATE_FOLDER'], 'jesmond/'])
    my_loader = jinja2.ChoiceLoader([                                                
	    jinja2.FileSystemLoader(templatepath),                  
	    app.jinja_loader,                                                        
	])                                                                           
    app.jinja_loader = my_loader                                                     
    app.static_folder = app.config['STATIC_FOLDER']  
