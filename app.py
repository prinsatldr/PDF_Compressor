from flask import (
    Flask,
    render_template,
    request,
    send_from_directory
)

import os

from werkzeug.utils import secure_filename

from compress import compress_pdf


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    COMPRESSED_FOLDER,
    exist_ok=True
)


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/compress",
    methods=["POST"]
)
def compress():

    if "pdf" not in request.files:
        return "No PDF uploaded"

    file = request.files["pdf"]

    if file.filename == "":
        return "No file selected"

    filename = secure_filename(
        file.filename
    )

    mode = request.form.get(
        "mode",
        "balanced"
    )

    input_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(input_path)

    compressed_filename = (
        "compressed_" + filename
    )

    output_path = os.path.join(
        COMPRESSED_FOLDER,
        compressed_filename
    )

    result = compress_pdf(
        input_path,
        output_path,
        mode
    )

    return render_template(
        "index.html",
        result=result,
        filename=filename,
        mode=mode,
        download_file=compressed_filename
    )


@app.route(
    "/download/<filename>"
)
def download(filename):

    return send_from_directory(
        COMPRESSED_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )