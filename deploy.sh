#!/bin/sh
git push -u origin master
git push heroku master
heroku scale web=1
heroku open
