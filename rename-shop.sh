#!/bin/bash
set -x # Prints each command before executing it
set -e # Exit the script immidietly if an error happens

# Usage:
# ./rename-shop.sh <old-name> <new-name>
#


OLD_NAME=$1
NEW_NAME=$2
DOMAIN="subscriby.shop"
INI_FILE="subscriby.shop.ini"

echo Old name: $OLD_NAME
echo New name: $NEW_NAME

# Check that the new-name does not already exist
if [ -d $NEW_NAME.$DOMAIN ]
then
  echo "$NEW_NAME.subscriby.shop already exists"
  exit 1
fi
# this will only be uselfull for admins if not is useless OLD name will be requested
#if [ ! -d $OLD_NAME.$DOMAIN  ]
#then
#  echo "$OLD_NAME may be misspelled"
#  exit 1
#fi

# Rename the directory from old-name to new-name
mv $OLD_NAME  $NEW_NAME.$DOMAIN #rename directory
mv $NEW_NAME.$DOMAIN/$OLD_NAME.ini $NEW_NAME.$DOMAIN/$NEW_NAME.$INI_FILE #rename ini file

# Update the .ini file
sed -i.bk "s/$OLD_NAME/$NEW_NAME/g" $NEW_NAME.$DOMAIN/$NEW_NAME.$INI_FILE 
# Update the .env file
sed -i.bk "s/$OLD_NAME/$NEW_NAME/g" $NEW_NAME.$DOMAIN/.env
# Rename the .ini file, without this, the uwsigi server keeps the old config
mv $NEW_NAME.$DOMAIN/$NEW_NAME.$INI_FILE $NEW_NAME.$DOMAIN/$NEW_NAME.disabled
mv $NEW_NAME.$DOMAIN/$NEW_NAME.disabled $NEW_NAME.$DOMAIN/$NEW_NAME.$INI_FILE

