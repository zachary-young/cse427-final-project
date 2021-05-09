from flask import Flask, render_template, request, send_file, session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os

app = Flask(__name__, template_folder='../client/template', static_folder='../client/static')
app.secret_key = '\x17Y\x98\x10!\x9c"\x11\t\x14\x03v\xa1\x1c\xc2\x07|\xdd\xc2H\xde\x9f\x9b\x19'
uploads_dir = os.path.join(app.instance_path, 'files')


@app.route('/')
def home():
    return render_template("index.html")
    
#stores uploaded file
@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['myFile']
        session["fileName"] = secure_filename(f.filename)
        print(uploads_dir)
        f.save(os.path.join(uploads_dir, secure_filename(f.filename)))
        return render_template("index.html")

#sends file back to user
@app.route('/downloader')
def download_file():
    return send_file("instance/files/"+session["fileName"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


