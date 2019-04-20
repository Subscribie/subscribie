Single node couchdb instance to support site submissions
from a Subscribie site with the builder module installed.
```
kubectl apply -f subscribie-k8s-pod.yaml
kubectl apply -f subscribie-k8s-service.yaml
kubectl apply -f couchdb-k8s-pod.yaml
```
