#/usr/bin/env bash
source .env

if [ "$ENV" == "production" ]
then
    echo "In production usin mod_wsgi, reloading apache2"
    sudo service apache2 reload
else
    echo "hedgehog is in development mode. Starting simple python server..."
    sudo python shortly.py
fi

