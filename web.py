import os
from flask import Flask, request, redirect, url_for, flash, render_template, send_from_directory
from werkzeug import secure_filename
import pHash
import csv

from pymongo import Connection
connection = Connection('staff.mongohq.com',10045)
db = connection.app1936919
db.authenticate('heroku','herokuapp')
collection = db.art

CATALOG = "./hash-catalog.csv"

UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

head = "<html><head><title>Query Results</title><style>body {margin:50px 0px; padding:0px;text-align:center;}</style>"
head += "</head><body><div><h1>Query Results</h1><p><h2>These are possible results based on your image query</h2></p><table>"
 
foot = "</table><h2>Not here? Try another image.</h2><form>"
foot +="<INPUT TYPE=\"BUTTON\" VALUE=\"Click Here\" ONCLICK=\"window.location.href=\'http://artbybit.herokuapp.com\'\"> </form></div> </body></html>"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
         file = request.files['file']
         if file and allowed_file(file.filename):
             filename = secure_filename(file.filename)
             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
             return redirect(url_for('results', filename=filename))
    return render_template('upload.html')

@app.route('/results/<filename>')
def results(filename):
    image = app.config['UPLOAD_FOLDER']+ "/" + filename
    h1 = pHash.avhash(image)
    os.remove(image)
    reader = csv.reader(open(CATALOG, "rb"), delimiter=";")
    body = ""
    for author, life, title, date, hash, technique, location, url, form, type in reader:
        h2 = int(hash)
        distance = pHash.hamming(h1,h2)
        if distance < 9:
            body+= "<tr><td>Title</td><td><h3>" + title + "</h3></td></tr>"
            body+= "<tr><td>Masterpiece</td><td><img src = \"" +url + "\" /></td></tr>"
            body+= "<tr><td>Author</td><td>" + author + "</td></tr>"
            body+= "<tr><td>Date</td><td>" + date + "</td></tr>"
            body+= "<tr><td>Technique</td><td>" + technique + "</td></tr>"
            body+= "<tr><td>Current Location</td><td>" + location + "</td></tr>"
            body+= "<tr><td>Form</td><td>" + form + "</td></tr>"
            body+= "<tr><td>Type</td><td>" + type + "</td></tr>"
    if len(body) > 0:
        return head + body + foot
    else:
        return render_template('not_found.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
