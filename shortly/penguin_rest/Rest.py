import requests
import os
import json
from flask import current_app as app

def post(fields='', entity=''):
    print "Posting to penguin!"

    #Get CSRF token
    token = str(requests.get(app.config['PENGUIN_URL'] + '/session/token').text)

    endpoint = app.config['PENGUIN_URL'] + "/node?_format=hal_json"
    entity_href = ''.join(['"', app.config['PENGUIN_URL'], '/rest/type/node/', entity,'"'])
    # Replace https with http for entity href only (endpoint remains https)
    entity_href = entity_href.replace('https','http')

    def format_fields(fields):
	fields_formatted = {}
	for index, value in enumerate(fields):
	    fields_formatted[value] = [{"value": fields[value]}]
	#Convert to json
	fields_formatted = json.dumps(fields_formatted)
	#Remove outer brackets and return
	return fields_formatted[1:-1]

    #Set all required headers
    headers = {'Content-Type':'application/hal+json',
	'X-CSRF-Token':token
    }

    #Include all fields required by the content type
    payload  = '''
    {
    "_links": {
    "type": {
    "href": '''
    payload = payload + entity_href
    payload = payload + '''
    }
    },'''
    payload = payload + format_fields(fields) + '''
    }'''

    #Post the new node (a Contact) to the endpoint.
    user = app.config['REST_USER']
    password = app.config['REST_PASSWORD']
    r = requests.post(endpoint, data=payload, headers=headers, auth=(user,password))

    #Check was a success 
    if r.status_code == 201:
	print "Success"
        print r.text
    else:
	print "Fail"
	print r.status_code
        print r.text
