#! /bin/bash
set -euxo pipefail

export FLASK_APP=subscribie
export FLASK_DEBUG=1

if [ -a .env ]
then
  echo ".env exists already so not copying from .env.example"
else
  echo ".env not found, so copying from .env.example"
  cp .env.example .env
fi

# Set DB URI & PATH
sed -i 's#SQLALCHEMY_DATABASE_URI.*#SQLALCHEMY_DATABASE_URI="sqlite:////usr/src/app/data.db"#g' .env
sed -i 's#DB_FULL_PATH.*#DB_FULL_PATH=/usr/src/app/data.db#g' .env

# Set cookie secure flag to false in development
sed -i 's#SESSION_COOKIE_SECURE.*##g' .env
sed -i 's#SESSION_COOKIE_SAMESITE.*#Lax#g' .env

# Remove SERVER_NAME app config in docker environment
sed -i 's#SERVER_NAME.*##g' .env

# Set static dir
sed -i 's#TEMPLATE_BASE_DIR.*#TEMPLATE_BASE_DIR=/usr/src/app/subscribie/subscribie/themes/#g' .env
sed -i 's#UPLOADED_IMAGES_DEST.*#UPLOADED_IMAGES_DEST=/usr/src/app/subscribie/subscribie/static/#g' .env

flask db upgrade

flask initdb

exec uwsgi --http :80 --workers 1 --threads 2 --wsgi-file subscribie.wsgi --touch-chain-reload subscribie.wsgi --chdir /usr/src/app/subscribie/

