import sys
import os
import logging

PYTHON_LOG_LEVEL = os.getenv('PYTHON_LOG_LEVEL', logging.INFO)

logging.basicConfig(level=PYTHON_LOG_LEVEL)

def load():
    path_inject = os.getenv('PYTHON_PATH_INJECT')
    if path_inject is not None:
        logging.info(f"Injecting python path {path_inject}")
        sys.path.insert(0, path_inject)

load()

from subscribie import create_app

application = create_app()
