import os
import requests
import json
import yaml
import subprocess
import shutil
from pathlib import Path


def bootstrap_needed():
    if (
        os.getenv("SUBSCRIBIE_FETCH_JAMLA") is not None
        and os.path.isfile("/subscribie/volume/bootstrap_complete") is False
    ):
        print("NOTICE: bootstrap requested")
        return True
    else:
        print(
            "NOTICE: bootstrap not possible because marked as complete,\
          or `export SUBSCRIBIE_FETCH_JAMLA=True` not set"
        )
        return False


def bootstrap_possible():
    """ Check if we have all environment vars needed to bootstrap 
    - Can we contact the remote jamla manifest (couchdb)
    - Do we have a shop name?
  """

    def env_is_set(name):
        if os.getenv(name) is None:
            print("{} not set".format(name))
            return False

    needed = [
        "COUCH_DB_SERVICE_NAME",
        "COUCHDB_USER",
        "COUCHDB_PASSWORD",
        "COUCHDB_DBNAME",
        "SUBSCRIBIE_SHOPNAME",
    ]
    missing = []
    for envname in needed:
        if env_is_set(envname) is False:
            missing.append(envname)
        if len(missing) is not 0:
            print("Cannot bootstrap")
            return False
    return True


def get_couchdb_con():
    COUCHDB_USER = os.getenv("COUCHDB_USER", "admin")
    COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD", "password")
    # If running within cluster, address couchdb by its service name
    if "COUCH_DB_SERVICE_NAME" in os.environ:
        HOST = "".join(
            [
                "http://{}:{}".format(COUCHDB_USER, COUCHDB_PASSWORD),
                "@",
                os.getenv("COUCH_DB_SERVICE_NAME"),
                ":5984/",
            ]
        )
    else:
        HOST = "http://{}:{}@127.0.0.1:5984/".format(COUCHDB_USER, COUCHDB_PASSWORD)

    DBNAME = os.getenv("COUCHDB_DBNAME")
    COUCHDB = HOST + "/" + DBNAME
    return COUCHDB


def bootstrap(app):
    """
  Bootstrap a subscribie site whereby the Jamla manifest
  is to be consumed from an external source e.g. a couchdb
  database. We assume a persistant volume is present at path
  "/subscribie/volume" this is used to store the Jamla manifest
  and also mark as bootstrap completed by dropping an empty file
  'bootstrap_complete' in /subscribie/volume.

    - Work out if we need to bootstrap 
      - By checking for SUBSCRIBIE_FETCH_JAMLA environment var
      - and by checking if exists /subscribie/volume/bootstrap_complete
    - Fetch Jamla manifest from external source (assume couchdb)
    - Perform bootstrap
      - Inject Jamla manifest to /subscribie/volume/jamla.yaml
      - Update jamla path in config.py
      - Inject static assets (images, if any, from couchdb attachments) 
    - Copy config.py to /subscribie/volume/config.py
    - Mark as bootstrapped
    - continue running as normal
  """
    if bootstrap_needed() and bootstrap_possible():
        print("NOTICE: bootstrapping site")
        shopName = os.getenv("SUBSCRIBIE_SHOPNAME")
        # Fetch jamla from couchdb
        COUCHDB_CON = get_couchdb_con()
        req = requests.get(COUCHDB_CON + "/" + shopName)
        if req.status_code == 200:
            # Inject Jamla manifest
            jamla = yaml.dump(req.json())
            # Write jamla.yaml to PersistentVolume
            with open("/subscribie/volume/jamla.yaml", "w+") as fp:
                fp.write(jamla)
            # Parse jamla back to dict
            jamla = yaml.load(jamla)
            # Move themes to persistant volume
            dst = "/subscribie/volume/themes"
            if os.path.exists(dst) is False:
                shutil.move("./themes", dst)
                # Fetch and inject any static assets (uploaded images)
                req = requests.get(COUCHDB_CON + "/" + shopName)
                resp = req.json()
                if "_attachments" in resp:
                    attachments = resp["_attachments"]
                    for key, value in attachments.items():
                        attachment = requests.get(
                            COUCHDB_CON + "/" + shopName + "/" + key, stream=True
                        )
                        attachmentDst = (
                            "/subscribie/volume/themes/theme-{}/static/".format(
                                jamla["theme"]["name"]
                            )
                            + key
                        )
                        with open(attachmentDst, "wb") as fp:
                            shutil.copyfileobj(
                                attachment.raw, fp
                            )  # Store attachment in theme static folder
            else:
                print("NOTICE: {} already present so not overwriting".format(dst))

            # Update jamla path and template folder path
            db_full_path = "/subscribie/volume/data.db"
            template_base_dir = "/subscribie/volume/themes/"
            static_folder = "{template_base_dir}theme-{theme_name}/static/".format(
                template_base_dir=template_base_dir, theme_name=jamla["theme"]["name"]
            )
            subprocess.call(
                "subscribie \
               setconfig --JAMLA_PATH /subscribie/volume/jamla.yaml \
               --DB_FULL_PATH {db_full_path}\
               --TEMPLATE_BASE_DIR {template_base_dir}\
               --STATIC_FOLDER {static_folder}".format(
                    db_full_path=db_full_path,
                    template_base_dir=template_base_dir,
                    static_folder=static_folder,
                ),
                shell=True,
            )
            # Move config file to persistant volume
            path = os.path.abspath(__file__ + "../../../instance")
            print("Copying config.py from: {}".format(path))
            shutil.copy(path + "/config.py", "/subscribie/volume/")

            # Move database file to persistant volume
            path = os.path.abspath(__file__ + "../../../")
            print("Copying data.db from: {}".format(path))
            shutil.copy(path + "/data.db", "/subscribie/volume/")

            # Mark site as bootstrapped
            path = Path("/subscribie/volume/bootstrap_complete")
            path.touch(exist_ok=True)
        elif req.status_code == 404:
            print("Could not locate jamla manifest from couchdb")
            exit()
