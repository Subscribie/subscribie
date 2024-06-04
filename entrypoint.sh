#! /bin/bash
set -euxo pipefail

export FLASK_APP=subscribie
export FLASK_DEBUG=1

if [ -a settings.yaml ]
then
  echo "settings.yaml exists already so not copying from settings.yaml.example"
else
  echo "settings.yaml not found, so copying from settings.yaml.example"
  cp settings.yaml.example settings.yaml
  if [ ! -d "modules" ]; then
    echo creating modules directory because it didn\'t exit
    mkdir modules
  fi

  # Set DB URI & PATH
  sed -i 's#SQLALCHEMY_DATABASE_URI.*#SQLALCHEMY_DATABASE_URI: "sqlite:////usr/src/app/data.db"#g' settings.yaml
  sed -i 's#DB_FULL_PATH.*#DB_FULL_PATH: "/usr/src/app/data.db"#g' settings.yaml

  # Set static dir
  sed -i 's#TEMPLATE_BASE_DIR.*#TEMPLATE_BASE_DIR: "/usr/src/app/subscribie/subscribie/themes/"#g' settings.yaml
  sed -i 's#UPLOADED_IMAGES_DEST.*#UPLOADED_IMAGES_DEST: "/usr/src/app/subscribie/subscribie/static/"#g' settings.yaml
fi


flask db upgrade

flask initdb

exec uwsgi --http :80 --workers 1 --threads 2 --wsgi-file subscribie.wsgi --touch-chain-reload subscribie.wsgi --chdir /usr/src/app/subscribie/

