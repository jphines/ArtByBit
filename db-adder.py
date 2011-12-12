import csv
import pHash
import os
from pymongo import Connection

connection = Connection('staff.mongohq.com',10045)
db = connection.app1936919
db.authenticate('heroku','herokuapp')
collection = db.art

reader = csv.reader(open("testcat.csv", "rb"), delimiter=";")

for author, life, title, date, hash, technique, location, url, form, type in reader:
    masterpiece = {'Artist': author, 'Born-Died': life, 'Title': title, 'Date': date, 'Hash': hash, 'Technique': technique, 'Location': location, 'URL': url, 'Form': form, 'Type': type}
    collection.insert(masterpiece)
    
print "Done!"
