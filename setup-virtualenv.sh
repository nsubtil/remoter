#!/bin/sh

virtualenv -p /usr/local/Cellar/python/2.7.9/bin/python python-env
python-env/bin/pip install -r requirements.txt

