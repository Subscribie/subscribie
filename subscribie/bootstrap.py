import os
import requests
import json
import yaml
import subprocess
import shutil
from pathlib import Path
import sqlite3
import datetime


def bootstrap_needed():
    print("NOTICE: bootstrap requested")
    fail = False
    if os.getenv("SUBSCRIBIE_FETCH_JAMLA") is None:
      print("NOTICE: SUBSCRIBIE_FETCH_JAMLA is not set, refusing to bootstrap.")
      fail = True
    if os.path.isfile("/subscribie/volume/bootstrap_complete") is True:
      print("/subscribie/volume/bootstrap_complete already exists")
      fail = True
    if fail is True:
      print("NOTICE: bootstrap not possible. Either already complete or \
              SUBSCRIBIE_FETCH_JAMLA not set.")
      return False
    return True


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
  database. We assume a persistant volume is attatched at path
  "/subscribie/volume" this is used to store:
    - The Jamla manifest specific to this site
    - The data.db sqlite3 database for the admin user
    - To mark site a bootstrap completed by creating an empty file
      'bootstrap_complete' in /subscribie/volume.
  The bootstrap works as follows:
    - Work out if we need to bootstrap 
      - By checking for SUBSCRIBIE_FETCH_JAMLA environment var
      - and by checking if exists /subscribie/volume/bootstrap_complete
    - Fetch Jamla manifest from external source (assume couchdb)
    - Perform bootstrap:
      - Inject Jamla manifest to /subscribie/volume/jamla.yaml
      - Update jamla path in config.py
      - Inject static assets (images, if any, from couchdb attachments) 
      - Copy config.py to /subscribie/volume/config.py
      - Inject user's email address into data.db (email is in the jamla
        manifest
      - Mark as bootstrapped
      - Continue running as normal
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

            # Move database file to persistant volume
            path = os.path.abspath(__file__ + "../../../")
            print("Copying data.db from: {}".format(path))
            shutil.copy(path + "/data.db", "/subscribie/volume/")
            db_full_path = "/subscribie/volume/data.db"

            # Update jamla path and template folder path
            template_base_dir = "/subscribie/volume/themes/"
            static_folder = "{template_base_dir}theme-{theme_name}/static/".format(
                template_base_dir=template_base_dir, theme_name=jamla["theme"]["name"]
            )

            # Run subscribie_cli database migrations
            subprocess.call('subscribie migrate --DB_FULL_PATH ' + db_full_path,
                            shell=True)


            # Inject user's (site owners) email address into the data.db
            for email in jamla['users']:
              #TODO use subscribie cli for injecting the user.
              con = sqlite3.connect(db_full_path)
              con.text_factory = str
              cur = con.cursor()
              now = datetime.datetime.now()
              login_token = ''
              cur.execute("INSERT INTO user (email, created_at, active, login_token) VALUES (?,?,?,?)",
                         (email, now, 1, login_token,))
              con.commit()
              con.close()
            # Set subscribie config for db path, template dir, static folder
            uploaded_images_dest="/subscribie/volume/static/"
            subprocess.call(
                "subscribie \
               setconfig --JAMLA_PATH /subscribie/volume/jamla.yaml \
               --DB_FULL_PATH {db_full_path}\
               --TEMPLATE_BASE_DIR {template_base_dir}\
               --STATIC_FOLDER {static_folder}\
               --UPLOADED_IMAGES_DEST {uploaded_images_dest}\
               --MAIL_SERVER {mail_server}\
               --MAIL_DEFAULT_SENDER {mail_default_sender}\
               --EMAIL_LOGIN_FROM {email_login_from}\
               --MAIL_PORT {mail_port}\
               --MAIL_USE_TLS {mail_use_tls}\
               --MAIL_USERNAME {mail_username}\
               --MAIL_PASSWORD {mail_password}".format(
                    db_full_path=db_full_path,
                    template_base_dir=template_base_dir,
                    static_folder=static_folder,
                    uploaded_images_dest=uploaded_images_dest,
                    mail_server=os.getenv('MAIL_SERVER'),
                    mail_default_sender=os.getenv('MAIL_DEFAULT_SENDER'),
                    email_login_from=os.getenv('EMAIL_LOGIN_FROM'),
                    mail_port=os.getenv('MAIL_PORT'),
                    mail_use_tls=os.getenv('MAIL_USE_TLS'),
                    mail_username=os.getenv('MAIL_USERNAME'),
                    mail_password=os.getenv('MAIL_PASSWORD') 
                ),
                shell=True,
            )
            # Move config file to persistant volume
            path = os.path.abspath(__file__ + "../../../instance")
            print("Copying config.py from: {}".format(path))
            shutil.copy(path + "/config.py", "/subscribie/volume/")

            # Create uploaded_images_dest directory
            os.makedirs(uploaded_images_dest, exist_ok=True)

            # Mark site as bootstrapped
            path = Path("/subscribie/volume/bootstrap_complete")
            path.touch(exist_ok=True)
        elif req.status_code == 404:
            print("Could not locate jamla manifest from couchdb")
            exit()
