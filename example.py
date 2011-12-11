import csv
import pHash

reader = csv.reader(open("test.csv", "rb"), delimiter=";")

writer = csv.writer(open("testdata.csv","wb"), delimiter=";")

fields = reader.next()

for author, life, title, date, technique, location, url, form, type, school, time in reader:
    words = url.split("/")
    filename = "./http___www.wga.hu_art_
    imagename = words.pop()
    image = imagename.split(".")
    imagename = "/" + image.index(0) + ".jpg"
    popped = words.pop()
    end = ""
    while popped != "html"
        end = "_" + popped + "_" + end
        popped = words.pop()
    filename += end
    filename += imagename
    hash = avhash(filename)
    hashed = str(hash)


        





