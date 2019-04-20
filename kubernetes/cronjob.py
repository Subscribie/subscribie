import requests
import json
import random
import re
import subprocess
from kubernetes import client, config
import yaml
import tempfile




HOST = "http://admin:password@127.0.0.1:5984/jamlas"

def getDoc(docId):
  ''' Return doc from Couchdb 
  docId: Document id
  returns: Complete doc (excluding attachments)
  '''
  req = requests.get(HOST + '/' + docId)
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
  import pdb;pdb.set_trace()
  return rsp

req = requests.get(HOST + '/_all_docs')
resp = json.loads(req.text)
try:
  # Get a (TODO non-deployed) document at random , it dosent matter.
  docRow = random.choice(resp['rows'])
  manifest = generateManifest(docRow['id'])
  response = deployManifest(manifest)
except IndexError:
  print("Do documents left to process")

  



  
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
