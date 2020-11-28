#! /bin/bash
set -euxo pipefail

export FLASK_APP=subscribie
export FLASK_DEBUG=1

flask db upgrade

flask initdb

exec uwsgi --http :80 --workers 1 --wsgi-file subscribie.wsgi --touch-chain-reload subscribie.wsgi --chdir /usr/src/app/subscribie/

