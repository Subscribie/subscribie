#! /bin/sh
kubectl delete deployment/couchdb-deployment
kubectl delete deployment subscribie-onboarding-deployment
kubectl delete pvc couchdb-volume-claim
kubectl delete pvc subscribie-onboarding-volume
kubectl delete pod/cronpod
