#!/bin/sh

virtualenv -p /usr/local/bin/python python-env
python-env/bin/pip install -r requirements.txt

