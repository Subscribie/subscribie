from .jamla import Jamla
import jinja2
import os


def load_theme(app):
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])

    try:
        if os.path.isdir(jamla['theme']['name']):
            #Allow theme path to be specified as absolute path
            themepath = jamla['theme']['name']
        else:
            #Most client code will pass theme by name
            themepath = ''.join([app.config['TEMPLATE_FOLDER'], 
                                 'theme-', 
                                 jamla['theme']['name'], '/',
                                 jamla['theme']['name']])
        if os.path.exists(themepath) is False:
            raise
    except Exception as e:
        print "Falling back to default theme"
        print e
        themepath =  app.config['TEMPLATE_FOLDER'] + 'jesmond' 
        themepath = os.path.dirname(os.path.realpath(__file__)) + "/templates/jesmond/"
    my_loader = jinja2.ChoiceLoader([                                                
	    jinja2.FileSystemLoader(themepath),                  
	    app.jinja_loader,                                                        
	])                                                                           
    app.jinja_loader = my_loader                                                     
    app.static_folder = jamla['theme']['static_folder']
