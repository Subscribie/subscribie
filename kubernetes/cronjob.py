import requests
import json
HOST = "http://admin:password@127.0.0.1:5984/jamlas/_all_docs"
# Get a document
'''
  - at random , it dosent matter.
'''
requests.get(HOST)


  
# Generate manifest
'''
  - label with document id from couchdb
  - deployment? Probably.
  - just pod?
  - storage? Ceph?
'''
# Submit manitest to kubernestes
'''
  - kubectl apply -f <>.yaml
'''

# Verify deployment is OK
'''
  - if deployment is OK
    - Delete document from couchdb
      - or mark as complete? NO this leaves mess. Just force client to retry
'''
# Report back to client this is sucess
'''
  - HOW?!?!?
    - Using email address in the manifest ~ easy
    - Dropping a new document into couchdb with <sitename>=completed, with
      its address, which the client can poll. Simple.
'''
