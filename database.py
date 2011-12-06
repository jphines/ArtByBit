#!/usr/bin/python
from pymongo import Connection
connection = Connection('staff.mongohq.com',10045)
db = connection.app1936919
db.authenticate('heroku','herokuapp')
collection = db.art
print collection.find_one()
