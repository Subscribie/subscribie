#/usr/bin/env bash
source .env

if [ "$ENV" == "production" ]
then
    echo "In production usin mod_wsgi, reloading apache2"
    sudo service apache2 reload
else
    echo "hedgehog is in development mode. Starting simple python server..."
    export FLASK_DEBUG=1
    export HEDGEHOG_ENV=./.env
    export FLASK_APP=__init__.py
    flask run
fi

