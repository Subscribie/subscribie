# Local builder module development

Steps to quickly get Subscribie + builder module running on localhost
for development. Without kubernetes needed. 

Allows you to test the builder module locally

- couchdb (the builder module needs this to submit new site manifests to)
- Subscribie 
- builder theme
- builder module

## Couchdb setup 
Run a couch db instance using docker:

```
docker run --network host --name couchdb -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password -d couchdb
```
To remove this image when you're done:
```
docker rm -f couchdb
```

## Start an instance of subscribie
```
git clone git@github.com:Subscribie/subscribie.git
cd subscribie
pip install -r requirements.txt
mkdir modules # for modules
virtualenv -p python3 venv
. venv/bin/activate
pip install subscribiecli
subscribie init
subscribie migrate
export FLASK_APP=subscribie
```

Set correct path for themes dir:
- Use full path terminated with '/'
```
subscribie setconfig --TEMPLATE_BASE_DIR <path/to/themes/dir/>
```

Correct modules path by editing jamla.yaml:
```
modules_path: '/path/to/modules/'
```

Add builder module:

- Edit `jamla.yaml` and put 'builder' to include:

```
modules: 
  - name: builder
    src: git@github.com:Subscribie/module-builder.git
```

Switch to builder theme (required by builder module)

- Edit `jamla.yaml` and switch to the 'builder' theme:

```
theme:
    name: builder 
    src: git@github.com:Subscribie/theme-builder.git
```

Set environment vars required for builder module:

```
# Builder module
export COUCHDB_ENABLED=True
export COUCH_DB_SERVICE_NAME=127.0.0.1
export COUCHDB_IP=127.0.0.1
export COUCHDB_PORT=5984
export COUCHDB_SCHEME='http://'
export COUCHDB_USER=admin
export COUCHDB_PASSWORD=password
export COUCHDB_DBNAME=jamlas
```

## Create required CouchDB database and views

Create required database:
```
export HOST=http://admin:password@127.0.0.1:5984
export COUCHDB_DBNAME=jamlas
curl -X PUT $HOST/$COUCHDB_DBNAME
# You should see: {"ok":true}
```

Create required view:
```
export HOST=http://admin:password@127.0.0.1:5984
export COUCHDB_DBNAME=jamlas
curl -X PUT $HOST/$COUCHDB_DBNAME/_design/sites-queue -d @./kubernetes/sites-pipeline/views.json
# You should see: {"ok":true,"id":"_design/sites-queue","rev":"1-abc123"}
```


Run Subscribie 
```
subscribie run
```

Remove:

```
deactivate
rm -rf subscribie
```
