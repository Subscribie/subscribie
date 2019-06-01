import requests
import json
import random
import re
import subprocess
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
import tempfile
from time import sleep
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)

from kubernetes import client, config


def loadClusterConfig():
    # Assume we're inside a kubernetes cluster
    try:
        config.load_incluster_config()
    except kubernetes.config.config_exception.ConfigException:
        # Assume localhost, Load config from localhost
        config.load_kube_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_namespaced_pod(namespace="default", watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


loadClusterConfig()

COUCHDB_USER = os.getenv("COUCHDB_USER", "admin")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD", "password")
# If running within cluster, address couchdb by its service name
if "COUCH_DB_SERVICE_NAME" in os.environ:
    HOST = "".join(
        [
            "http://{}:{}".format(COUCHDB_USER, COUCHDB_PASSWORD),
            "@",
            os.getenv("COUCH_DB_SERVICE_NAME"),
            ":5984",
        ]
    )
else:
    HOST = "http://{}:{}@127.0.0.1:5984".format(COUCHDB_USER, COUCHDB_PASSWORD)

DBNAME = "jamlas"
COUCHDB = HOST + "/" + DBNAME
WAITING_VIEW = COUCHDB + "/_design" + "/sites-queue" + "/_view" + "/waiting"


# create an instance of the API class
configuration = kubernetes.client.Configuration()
api_instance = kubernetes.client.CustomObjectsApi(kubernetes.client.ApiClient(configuration))

def generateCephFilesystemManifest(docId):
    """ Generate persistent volume claim manifest """
    # Generate manifest
    doc = getDoc(docId)
    siteName = formatSiteName(doc)

    manifest = {
      "apiVersion": "ceph.rook.io/v1",
      "kind": "CephFilesystem",
      "metadata": {
        "name": "site-storage-" + siteName,
        "namespace": "rook-ceph"
      },
      "spec": {
        "metadataPool": {
          "replicated": {
            "size": 2
          }
        },
        "dataPools": [
          {
            "replicated": {
              "size": 2
            }
          }
        ],
        "metadataServer": {
          "activeCount": 1,
          "activeStandby": True  # True not "true" as operator does not validate
        }
      }
    }
    return manifest

def deployCephFilesystemManifest(manifest):
  api_instance = kubernetes.client.CustomObjectsApi(kubernetes.client.ApiClient(configuration))
  group = 'ceph.rook.io' # str | the custom resource's group
  version = 'v1' # str | the custom resource's version
  namespace = 'rook-ceph'
  plural = 'cephfilesystems' # str | the custom object's plural name. For TPRs this would be lowercase plural kind.
  body = manifest # object | The JSON schema of the Resource to create.
  pretty = 'true' # str | If 'true', then the output is pretty printed. (optional)

  try: 
      api_response = api_instance.create_namespaced_custom_object(group, version, namespace, plural, body, pretty=pretty)
      pp.pprint(api_response)
  except ApiException as e:
      print("Exception when calling CustomObjectsApi->create_namespaced_custom_object: %s\n" % e)

def init():
    # Create required database
    req = requests.put(HOST + "/" + DBNAME)
    # Create required views
    # - waiting view
    # - completed view
    views = {
        "views": {
            "waiting": {
                "map": 'function (doc) {\n  if(doc.queue_state == "deploy") {\n  emit(doc._id, 1);\n  }\n}'
            },
            "completed": {
                "map": 'function (doc) {\n  if(doc.queue_state == "completed") {\n  emit(doc._id, 1);\n  }\n}'
            },
        },
        "language": "javascript",
    }
    req = requests.put(COUCHDB + "/_design/sites-queue", json=views)


init()  # Create required database and view(s)


def getDoc(docId):
    """ Return doc from Couchdb 
  docId: Document id
  returns: Complete doc (excluding attachments)
  """
    req = requests.get(COUCHDB + "/" + docId)
    resp = json.loads(req.text)
    return resp


def formatSiteName(doc):
    siteName = re.sub(r"\W+", "", doc["company"]["name"]).lower()
    return siteName


def generateManifest(docId):
    """ Generate Kubernetes manifest yaml from CouchDB document
  the attached jamla document is to be injected into the
  subscribie container, along with any environment vars
  needed. """
    pass
    # Generate manifest
    doc = getDoc(docId)
    try:
        siteName = formatSiteName(doc)
        deploymentName = siteName

        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": deploymentName,
                "labels": {
                    "subscribie": "site",
                    "sitename": siteName,
                    "docid": siteName,  # Doc id is the sitename
                },
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"subscribie": siteName}},
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "subscribie",
                            "subscribie": siteName,
                            "sitename": siteName,
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "subscribie",
                                "image": "subscribie/subscribie:v0.06",
                                "imagePullPolicy": "Always",
                                "ports": [
                                    {"name": "subscribie-port", "containerPort": 9090}
                                ],
                                "env": [
                                        {"name": "EXAMPLE", "value": "example_value"},
                                        {"name": "SUBSCRIBIE_SHOPNAME", "value": siteName},
                                        {"name": "SUBSCRIBIE_FETCH_JAMLA", "value":"couchdb"},
                                        {"name": "COUCH_DB_SERVICE_NAME", "value": "couchdb-service"},
                                        {"name": "COUCHDB_USER", "value": "admin"},
                                        {"name": "COUCHDB_PASSWORD", "value": "password"},
                                        {"name": "COUCHDB_DBNAME", "value": "jamlas"},
                                        {"name": "COUCHDB_PASSWORD", "value": "password"}
                                ],
                                "volumeMounts": [
                                    {
                                        "name": siteName + "-static",
                                        "mountPath": "/subscribie/volume",
                                    }
                                ],
                            }
                        ],
                        "volumes": [
                            {
                                "name": siteName + "-static",
                                "flexVolume": {
                                  "driver": "ceph.rook.io/rook",
                                  "fsType": "ceph",
                                  "options": {
                                    "fsName": "site-storage-" + siteName,
                                    "clusterNamespace": "rook-ceph"
                                  }
                                }
                            }
                        ],
                    },
                },
            },
        }
        return manifest
    except KeyError:
        print("Error could not parse site jamla. (KeyError)")
        return False
    """
    - storage? Ceph? No. Not ready for it. Possibly CouchDB, 
      just give clients an object store.
  """


def generatePVCManifest(docId):
    """ Generate persistent volume claim manifest """
    # Generate manifest
    doc = getDoc(docId)
    siteName = formatSiteName(doc)

    manifest = {
        "kind": "PersistentVolumeClaim",
        "apiVersion": "v1",
        "metadata": {"name": siteName + "-static"},
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "volumeMode": "Filesystem",
            "resources": {"requests": {"storage": "1Gi"}},
        },
    }
    return manifest


def generateServiceManifest(docId):
    """ Generate service manifest"""
    # Generate manifest
    doc = getDoc(docId)
    siteName = formatSiteName(doc)
    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": siteName + "-service"},
        "spec": {
            "selector": {
                "sitename": siteName  # Map service to specific subscribie site
            },
            "ports": [
                {
                    "name": "http",
                    "protocol": "TCP",
                    "port": 80,
                    "targetPort": "subscribie-port",
                }
            ],
            "type": "ClusterIP",
        },
    }
    return manifest


def generateIngressManifest(docId):
    """
    Generate Ingress manifest for a site
    - assumes subscribie.shop subdomain (for now)
    - The important mapping of service->pods is in "serviceName"
      - The service name is siteName + '-service'
    - This expects that cert-manager installed and working on your cluster
    - This ASSUMES you've checked and validated your cert-manager with issuer
      letsencrypt-staging manually first, rather than letsencrypt-prod
  """
    doc = getDoc(docId)
    siteName = formatSiteName(doc)
    manifest = {
        "apiVersion": "extensions/v1beta1",
        "kind": "Ingress",
        "metadata": {
            "name": siteName + "-ingress",
            "annotations": {
                "kubernetes.io/ingress.class": "nginx",
                "certmanager.k8s.io/issuer": "letsencrypt-prod",
                "certmanager.k8s.io/acme-challenge-type": "http01",
            },
        },
        "spec": {
            "rules": [
                {
                    "host": siteName + ".subscribie.shop",
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "backend": {
                                    "serviceName": siteName + "-service",
                                    "servicePort": 80,
                                },
                            }
                        ]
                    },
                }
            ],
            "tls": [
                {
                    "hosts": [siteName + ".subscribie.shop"],
                    "secretName": siteName + ".subscribie.shop-tls",
                }
            ],
        },
    }

    return manifest


def deployIngressManifest(manifest):
    v1 = client.ExtensionsV1beta1Api()
    try:
        rsp = v1.create_namespaced_ingress(namespace="default", body=manifest)
        return rsp
    except kubernetes.client.rest.ApiException as inst:
        errorBody = json.loads(inst.body)
        if errorBody["code"] == 409:  # Conflict
            print("NoOp. Ingress already exists")
        print(inst)


def deployServiceManifest(manifest):
    v1 = client.CoreV1Api()
    try:
        rsp = v1.create_namespaced_service(namespace="default", body=manifest)
        return rsp
    except kubernetes.client.rest.ApiException as inst:
        errorBody = json.loads(inst.body)
        if errorBody["code"] == 409:  # Conflict
            print("NoOp. Service already exists")
        print(inst)


def deployManifest(manifest):
    deployment = manifest
    v1 = client.AppsV1Api()
    rsp = v1.create_namespaced_deployment(body=deployment, namespace="default")
    return rsp


def deployPersistentVolumeClaim(manifest):
    v1 = client.CoreV1Api()

    try:
        rsp = v1.create_namespaced_persistent_volume_claim(
            namespace="default", body=manifest
        )
        return rsp
    except kubernetes.client.rest.ApiException as inst:
        errorBody = json.loads(inst.body)
        if errorBody["code"] == 409:  # Conflict
            print("NoOp. PersistentVolume already exists")
        print(inst)


def markDocCompleted(docId):
    # Get doc + revision
    req = requests.get(COUCHDB + "/" + docId)
    resp = json.loads(req.text)
    rev = resp["_rev"]
    # Mark as completed
    resp["queue_state"] = "completed"
    # Put updated doc
    req = requests.put(COUCHDB + "/" + docId, json=resp)


def consumeSites():
    try:
        req = requests.get(WAITING_VIEW)
        resp = json.loads(req.text)
        # Get a (TODO non-deployed) document at random , it dosent matter.
        docRow = random.choice(resp["rows"])
        # Generate storage
        fsManifest = generateCephFilesystemManifest(docRow["id"])
        print("#"*45)
        print(fsManifest)
        # Deploy storage
        deployCephFilesystemManifest(fsManifest)
        # Generate service & deploy
        manifest = generateServiceManifest(docRow["id"])
        print("#"*45)
        print(manifest)
        deployServiceManifest(manifest)
        # Generate and deploy deployment
        manifest = generateManifest(docRow["id"])
        print("#"*45)
        print(manifest)
        if manifest:
            try:
                deployManifest(manifest)
            except kubernetes.client.rest.ApiException as inst:
                errorBody = json.loads(inst.body)
                if errorBody["code"] == 409:  # Conflict
                    print("Deny. This site is already deployed")
                    markDocCompleted(docRow["id"])
                print(inst)
        # Generate Ingress & deploy Ingress
        manifest = generateIngressManifest(docRow["id"])
        deployIngressManifest(manifest)
        print("#"*45)
        print(manifest)

    except IndexError:
        print("Do documents left to process")
    sleep(1)
    consumeSites()  # Keep checking

consumeSites()


# Submit manifest to kubernestes

# Verify deployment is OK
"""
  - if deployment is OK
    - Delete document from couchdb
      - or mark as complete? NO this leaves mess. Just force client to retry
      - No. Mark it as deployed by updating the document. Allow attatchments for
        assets. Consider one couchbase database per user (DO IT)
"""
# Report back to client this is sucess
"""
  - HOW?!?!?
    - Using email address in the manifest ~ easy
    - Dropping a new document into couchdb with <sitename>=completed, with
      its address, which the client can poll. Simple.
"""
