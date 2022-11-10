#!/bin/bash

set -x
echo Checking docs are still live with curl
curl -s -o /dev/null -w "%{http_code}" https://docs.subscribie.co.uk
RET=$?

echo $RET

if [ $RET -ne 200 ]; then
  echo Could not curl docs url
  exit 255
fi
