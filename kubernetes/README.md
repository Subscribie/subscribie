## Subscribie Onboarding 
How to bring up onboarding system

- CouchDB (builder module submits to sites to couchdb)
- Builder Site (a subscribie site, with the builder module)
- cronpod (constantly polls couchdb for new sites to deploy, deploys them)

Single node couchdb instance to support site submissions
from a Subscribie site with the builder module installed.

### CouchDB
```
kubectl apply -f couchdb-k8s-pod.yaml
deployment.apps/couchdb-deployment created
persistentvolumeclaim/couchdb-volume-claim created
```

### Start cronpod
The cronpod constantly polls couchdb for new sites to deploy, and deploys them
by generating a valid kubernetes deployment manifest for each site found in 
couchdb, and submitts the manifest to kubernetes cluster using 
[https://github.com/kubernetes-client/python](python kubernetes client).

In order to create pods, create the service account for it:

```
kubectl apply -f sites-pipeline/subscribie-k8s-service-account-cronpod.yaml
```
Add the following roles to the cronpod service account:
```
## Create pod reader role
kubectl create role pod-reader --verb=get --verb=list --verb=watch --resource=pods
#### Bind it to the cronpod service account
kubectl create rolebinding cronpod-view \
--role=pod-reader \
--serviceaccount=default:cronpod \
--namespace=default
```

The cronpod deployment will 
- Constantly poll for new sites to be deployed by checking couchdb
- It will also create the required couchdb database and views required if they're not present in couchdb already
```
kubectl apply -f sites-pipeline/subscribie-k8s-cron-deployment.yaml
```

### Configure RBAC for cronpod

The cronpod needs permissions to put manifests to the kubernetes cluster
(deployments, ceph storage etc) in a controlled way. 

```
kubectl apply -f sites-pipeline/subscribie-k8s-rbac-deployments-create.yaml
kubectl apply -f sites-pipeline/subscribie-k8s-rbac-ingresses-create.yaml
kubectl apply -f sites-pipeline/subscribie-k8s-rbac-persistentvolumeclaims-create.yaml
kubectl apply -f sites-pipeline/subscribie-k8s-rbac-services-create.yaml
kubectl apply -f sites-pipeline/subscribie-k8s-rbac-pods.list.yaml
```

#### Post the subscribie site into couchdb
This will forward connections from your local machine into
the couchdb instance runnin on kubernetes.
```
kubectl port-forward service/couchdb-service 5988:5984
```
Then in a seperate terminal window:
Set `HOST` to the couchdb host with username and password:
```
HOST=http://admin:password@127.0.0.1:5988/jamlas
```
Patch users doc (not created automatically by docker image), fixes 
`ensure_auth_ddoc_exists/` error and others.:
```
curl -X PUT http://admin:password@127.0.0.1:5988/_users
curl -X PUT http://admin:password@127.0.0.1:5988/_replicator
curl -X PUT http://admin:password@127.0.0.1:5988/_global_changes #optional
```
Submit the subscribie-onboarding site into couchdb:
```
curl -X PUT $HOST/Subscribie -H "Content-Type: application/json" -d @jamla.json
{"ok":true,"id":"Subscribie","rev":"1-cf07243a3fe7fcb65830d962b87be08a"}
```

### Subscribie Onboarding Deployment 
This will ask kubernetes to deploy the subscribie-onboarding-deployment.
```
kubectl apply -f subscribie-k8s-filesystem.yaml # ceph back storage 
kubectl apply -f subscribie-k8s-onboarding-deployment.yaml
deployment.apps/subscribie-onboarding-deployment created
persistentvolumeclaim/subscribie-onboarding-volume created
```
### Deploy the subscribie service:
```
kubectl apply -f subscribie-k8s-service.yaml
```
### Expose onboarding website to ingress
Once you have set-up cert-manager for tsl termination:
( see for step-by-step see `from-scratch-empty-cluster.txt`)

Deploy staging cert (self signed)
```
kubectl apply -f subscribie-k8s-onboarding-ingress.yaml
```
To verify the certificate:
```
kubectl describe certificate start-subscribie-co-uk-secret
```
To change the certificate into a production one, edit the ingress
annotation `certmanager.k8s.io/issuer` from `letsencrypt-staging` to `prod`:
```
kubectl delete certificate start-subscribie-co-uk-secret # delete old cert
kubectl edit ingress subscribie-onboarding-ingress # and change from `letsencrypt-staging` to `prod`
```
After editing the ingress annotation, you should be able to access the site 
and see a valid tls certificate.

### Verify Deployment
View the pods:
```
kubectl get pods
NAME                                                READY   STATUS    RESTARTS   AGE
couchdb-deployment-6c8bf9ffb5-x2xfj                 1/1     Running   0          4m34s
cronpod                                             1/1     Running   2          4m27s
subscribie-onboarding-deployment-5c7d777d7f-zlkxn   1/1     Running   0          114s
```
View the services
```
kubectl get services
couchdb-service             ClusterIP      10.108.196.15   <none>        5984/TCP       3d19h
kubernetes                  ClusterIP      10.96.0.1       <none>        443/TCP        3d20h
subscribie-onboarding-svc   LoadBalancer   10.104.39.46    <pending>     80:32289/TCP   10h
```
View the logs from the subscribie-onboarding pod:
First get the name of the pod (with `kubectl get pods -l subscribie`)
then: 
```
kubectl logs -f subscribie-onboarding-deployment-<pod-id>
```

#### Debugging
##### Couchdb
Delete from couchdb. 
To delete from couchdb, you need to get the latest revision id first:
```  
curl -X GET $HOST/<site-name>
#Example:
curl -X GET $HOST/Subscribie
```
And then DELETE is, whilst passing the revision id:
```
curl -X DELETE $HOST/<site-name>?rev=<latest-rev-id>
#Example
curl -X DELETE $HOST/Subscribie?rev=1-54128f1ec2e39598b6a78244b5804cb9
```
