#!/bin/sh
virtualenv --no-site-packages .
source bin/activate
bin/pip install -r requirements.txt
foreman start
