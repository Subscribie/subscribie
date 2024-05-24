#!/bin/bash

set -exou

. .venv/bin/activate
python -m pytest
