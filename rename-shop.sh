#!/bin/bash
set -x # Prints each command before executing it
set -e # Exit the script immidietly if an error happens

# Usage:
# ./rename-shop.sh <old-domain> <new-name>
#

OLD_DOMAIN=$1
NEW_NAME=$2
NEW_DOMAIN=$NEW_NAME".subscriby.shop"
NEW_INI=$NEW_DOMAIN".ini"

echo Old name: $OLD_DOMAIN
echo New name: $NEW_DOMAIN

# Check that the new-name does not already exist
if [ -d $NEW_DOMAIN ]
then
  echo "$NEW_DOMAIN already exists"
  exit 1
fi
# this will only be uselfull for admins if not is useless OLD name will be requested
#if [ ! -d $OLD_DOMAIN  ]
#then
#  echo "$OLD_DOMAIN may be misspelled"
#  exit 1
#fi

# Rename the directory from old-name to new-name
mv $OLD_DOMAIN  $NEW_DOMAIN #rename directory
mv $NEW_DOMAIN/$OLD_DOMAIN.ini $NEW_DOMAIN/$NEW_INI #rename ini file

# Update the .ini file
sed -i.bk "s/$OLD_DOMAIN/$NEW_DOMAIN/g" $NEW_DOMAIN/$NEW_INI
# Update the .env file
sed -i.bk "s/$OLD_DOMAIN/$NEW_DOMAIN/g" $NEW_DOMAIN/.env
# Rename the .ini file, without this, the uwsigi server keeps the old config
mv $NEW_DOMAIN/$NEW_INI $NEW_DOMAIN/$NEW_NAME.disabled
mv $NEW_DOMAIN/$NEW_NAME.disabled $NEW_DOMAIN/$NEW_INI

