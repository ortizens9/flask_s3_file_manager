from flask import Flask, request, render_template
import logging
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"txt", "pdf", "jpg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


# get para mostrar formulario para seleccionar archivo,
# post para enviar los datos al servidor, en este caso para subir
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        message = ""
        f = request.files.get("the_file")
        if f and f.filename != "":
            secure_name = secure_filename(f.filename)
            if not allowed_file(secure_name):
                logging.warning("Object format not allowed")
                return render_template(
                    "upload.html", message="Error: Extension not allowed"
                )
            else:
                unique_name = f"{uuid.uuid4().hex}_{secure_name}"
                path = "uploads/" + unique_name
                f.save(path)
                message = f"File uploaded and saved: {unique_name}"
                return render_template("upload.html", message=message)
        else:
            logging.warning("Attempted to upload without providing a file")
            return render_template("upload.html", message="Error: Object not uploaded")


@app.route("/download")
def download():
    return "<p>Ruta para descargar objeto</p>"


@app.route("/delete")
def delete():
    return "<p>Ruta para borrar objeto</p>"


@app.route("/list")
def list_objects():
    return "<p>Ruta para listar objetos en un bucket</p>"


@app.route("/list_buckets")
def list_buckets():
    return "<p>Ruta para listar buckets</p>"


@app.route("/create_bucket")
def create_bucket():
    return "<p>Ruta para crear bucket</p>"
