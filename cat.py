import csv
import pHash
import os

reader = csv.reader(open("test.csv", "rb"), delimiter=";")

writer = csv.writer(open("testcat.csv","wb"), delimiter=";")

fields = reader.next()

for author, life, title, date, technique, location, url, form, type, school, time in reader:
    url = url.replace(".html",".jpg")
    url = url.replace("/html","/art")
    words = url.split("/")
    image = words.pop()
    os.system("wget " + url)
    hash = pHash.avhash(image)
    hashed = str(hash)
    os.remove(image)
    writer.writerow([author, life, title, date, hash, technique, location, url, form, type])
print "Done!"
