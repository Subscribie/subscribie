#!/usr/bin/env sh
git init # Start a git project (you might already have one, skip if you do)
git submodule add git@github.com:KarmaComputing/subscribie.git
cp subscribie/subscribie/jamla.yaml.example jamla.yaml
cp subscribie/subscribie/.env.example subscribie/subscribie/.env
#Set your jamla.yaml location by editing the .env file
sed -i s#JAMLA_PATH.*#JAMLA_PATH=\"$PWD/jamla.yaml\"#g subscribie/subscribie/.env
# Copy over default templates
cp -R subscribie/subscribie/templates ./
cp -R subscribie/subscribie/static ./
# Set template fallback base dir folder
sed -i s#TEMPLATE_FOLDER=.*#TEMPLATE_FOLDER=\"$PWD/templates/\"#g subscribie/subscribie/.env
# Set static dir
sed -i s#static_folder:.*#static_folder:\ \"$PWD/static/\"#g jamla.yaml
python subscribie/subscribie/createdb.py # Initalize database
# Run database migrations
for file in subscribie/subscribie/migrations/*; do ./$file -up -db "$PWD"/data.db; done
cp subscribie/subscribie/run.sh ./
sed -i s#FLASK_APP=#FLASK_APP=$PWD/subscribie/subscribie/#g run.sh
sed -i s#HEDGEHOG_ENV=.*#HEDGEHOG_ENV=$PWD/subscribie/subscribie/.env#g run.sh
