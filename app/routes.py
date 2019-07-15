import os
from app import app, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from app.adif import Adif
from flask import render_template, request, redirect, url_for
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Index page: upload an ADIF file
# -------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # No file specified
        if 'file' not in request.files:
            return render_template('error.html', error_title="Datei-Fehler",
                                   error_text="Keine Datei angegeben.")

        # File specified
        file = request.files['file']
        if file:
            # File allow
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('adif_file', filename=filename))
            # File not allowed
            else:
                return render_template('error.html', error_title="Datei-Fehler",
                                       error_text="Datei nicht erlaubt.")
    # Not 'POST' - upload page
    return render_template('index.html')


# ADIF page: show data from uploaded ADIF file and allow changes
# -------------------------------------------------------------------
@app.route('/adif/<filename>', methods=['GET', 'POST'])
def adif_file(filename):
    # Create Adif object from uploaded file
    try:
        adif_obj = Adif(path_to_file=os.path.join(UPLOAD_FOLDER, filename))
    except TypeError:
        return render_template('error.html', error_title="Datei-Fehler",
                               error_text="Datei '{}' kann nicht gelesen werden.".format(filename))

    # If 'POST', receive requested changes and apply them to the uploaded file
    if request.method == 'POST':
        changes = request.form
        deletes = changes.getlist('delete')
        renames = {}
        for key, value in changes.items():
            if key != 'delete' and value:
                renames[key] = value.lower()

        # Apply changes
        adif_obj.del_fields(deletes)
        adif_obj.change_names(renames)

        # Save changed ADIF file
        filename = adif_obj.save()

        return redirect(url_for('adif_file', filename=filename))

    # If not 'POST' display data from uploaded file
    else:
        return render_template('adif.html', adif=adif_obj)


# ADIF page: show the raw file
# -------------------------------------------------------------------
@app.route('/adif-view/<filename>')
def adif_view(filename):
    try:
        adif_obj = Adif(path_to_file=os.path.join(UPLOAD_FOLDER, filename))
    except TypeError:
        return render_template('error.html', error_title="Datei-Fehler",
                               error_text="Datei '{}' kann nicht gelesen werden.".format(filename))
    return render_template('adif-view.html', adif=adif_obj)


# Route to shutdown the server
# -------------------------------------------------------------------
@app.route('/shutdown')
def shutdown():
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    shutdown_server()
    return render_template('error.html', error_title="Programm beendet.",
                           error_text="Du kannst diesen Tab jetzt schließen.")
