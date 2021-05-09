from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from scipy.io import wavfile
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.instance_path, 'files')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['POST'])
def home():
    f = request.files["audio"]
    filename = secure_filename(f.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(filepath)
    samplerate, data = wavfile.read(filepath)
    return jsonify({"data": data.tolist()})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)


