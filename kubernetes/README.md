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

The cronpod will also create the required couchdb database and views required.
```
kubectl apply -f sites-pipeline/subscribie-k8s-cron-pod.yaml
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
Deploy the subscribie service:
```
kubectl apply -f subscribie-k8s-service.yaml
```

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
```
kubectl logs -f subscribie-onboarding-deployment-5c7d777d7f-zlkxn
```
If on minikube, you can view the subscribie-onboarding website in your browser:
```
minikube service subscribie-onboarding-svc
```
If you're on a real hosted kubernetes cluster (e.g. Google Cloud) just wait for 
an IP to appear in-place of `<pending>`. 


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
