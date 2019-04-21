import requests
import json
import random
import re
import subprocess
import kubernetes
from kubernetes import client, config
import yaml
import tempfile
from time import sleep


HOST = "http://admin:password@127.0.0.1:5984/"
DBNAME = "jamlas"
COUCHDB = HOST + '/' + DBNAME
WAITING_VIEW = COUCHDB + '/_design' + '/sites-queue' + '/_view' + '/waiting'

def init():
  # Create required database
  req = requests.put(HOST + '/' + DBNAME)
  # Create required views
  # - waiting view
  # - completed view
  views = {
      "views": {
        "waiting": {
          "map": "function (doc) {\n  if(doc.queue_state == \"deploy\") {\n  emit(doc._id, 1);\n  }\n}"
        },
        "completed": {
          "map": "function (doc) {\n  if(doc.queue_state == \"completed\") {\n  emit(doc._id, 1);\n  }\n}"
        }
      },
      "language": "javascript"
  }
  req = requests.put(COUCHDB + '/_design/sites-queue', json=views)
  
init() # Create required database and view(s)

def getDoc(docId):
  ''' Return doc from Couchdb 
  docId: Document id
  returns: Complete doc (excluding attachments)
  '''
  req = requests.get(COUCHDB + '/' + docId)
  resp = json.loads(req.text)
  return resp

def generateManifest(docId):
  ''' Generate Kubernetes manifest yaml from CouchDB document
  the attached jamla document is to be injected into the
  subscribie container, along with any environment vars
  needed. '''
  pass
  # Generate manifest
  doc = getDoc(docId)
  try:
    siteName = re.sub(r'\W+', '', doc['company']['name']).lower()
    deploymentName = siteName
    
    manifest = {
            'apiVersion': 'apps/v1', 
            'kind': 'Deployment', 
            'metadata': {
              'name': deploymentName, 
              'labels': {
                'subscribie': 'site',
                'sitename': siteName,
                'docid': siteName # Doc id is the sitename
              }
            }, 
            'spec': {
              'replicas': 2, 
              'selector': {
                'matchLabels': {
       
                  'subscribie': siteName}
              }, 
            'template': {
              'metadata': {
                'labels': {
                  'app': 'subscribie', 
                  'subscribie': siteName}
              }, 
              'spec': {
                'containers': [{
                  'name': 'subscribie', 
                  'image': 'subscribie/subscribie:v0.0.1', 
                  'imagePullPolicy': 'Always', 
                  'ports': [{'containerPort': 9090}], 
                  'env': [{
                    'name': 'EXAMPLE', 
                    'value': 'example_value'
                  }]
                }]
              }
            }
            }
        }
    return manifest
  except KeyError:
    print("Error could not parse site jamla. (KeyError)")
    return False
  '''
    - storage? Ceph? No. Not ready for it. Possibly CouchDB, 
      just give clients an object store.
  '''

def deployManifest(manifest):
  config.load_kube_config()
  deployment = manifest
  v1 = client.AppsV1Api()
  rsp = v1.create_namespaced_deployment(
          body=deployment, namespace="default")
  return rsp

def markDocCompleted(docId):
  # Get doc + revision
  req = requests.get(COUCHDB + '/' + docId)
  resp = json.loads(req.text)
  rev = resp['_rev']
  # Mark as completed
  resp['queue_state'] = "completed"
  # Put updated doc
  req = requests.put(COUCHDB + '/' + docId, json=resp)

def consumeSites():
  try:
    req = requests.get(WAITING_VIEW)
    resp = json.loads(req.text)
    # Get a (TODO non-deployed) document at random , it dosent matter.
    docRow = random.choice(resp['rows'])
    manifest = generateManifest(docRow['id'])
    if manifest:
      try:
        deployManifest(manifest)
      except kubernetes.client.rest.ApiException as inst:
        errorBody = json.loads(inst.body)
        if errorBody['code'] == 409: # Conflict
          print("Deny. This site is already deployed")
          markDocCompleted(docRow['id'])
        print(inst)
        
  except IndexError:
    print("Do documents left to process")
  sleep(1)
  consumeSites() # Keep checking

consumeSites()

  



  
# Submit manifest to kubernestes

# Verify deployment is OK
'''
  - if deployment is OK
    - Delete document from couchdb
      - or mark as complete? NO this leaves mess. Just force client to retry
      - No. Mark it as deployed by updating the document. Allow attatchments for
        assets. Consider one couchbase database per user (DO IT)
'''
# Report back to client this is sucess
'''
  - HOW?!?!?
    - Using email address in the manifest ~ easy
    - Dropping a new document into couchdb with <sitename>=completed, with
      its address, which the client can poll. Simple.
'''
