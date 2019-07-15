from flask import Flask

app = Flask(__name__)

UPLOAD_FOLDER = 'adif-files'
ALLOWED_EXTENSIONS = {'adi', 'adif', 'ADI', 'ADIF', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import routes
