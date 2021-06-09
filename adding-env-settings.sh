#! /bin/bash
# Please make sure you are in the right directory
#1. Run This Code with the new settings
#2. Merge the pull request (all sites will reload automatically)

PATH_TO_SITES=$2
KEYWORD=$1
if [ "$#" -ne 2 ]
  then
      echo "adding-settings-env.sh missing arguments"
      echo "Two arguments required"
      echo "Argument1 = newsetting='value'"
      echo "Argument2 = path/to/the/.env"
      echo "EXAMPLE"
      echo "./adding-settings-env.sh PATH_TO_SITES='/etc/home/' /etc/"
else      
    find $PATH_TO_SITES -maxdepth 2 -mindepth 2 -type f -name '.env' -exec  grep $KEYWORD {} +
    if [ $? -ne 0 ] 
      then 
         echo "Doesnt Exist, adding variable"
         find $PATH_TO_SITES -maxdepth 2 -mindepth 2 -type f -name '.env' -exec  sh -c "echo $KEYWORD >> {}" \;
         exit 0
    else
        echo "that setting already exists"
        exit 1
    fi
fi
