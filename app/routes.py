from flask import Blueprint, render_template, request, current_app
import logging
import uuid
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from .s3_client import S3Client

routes = Blueprint("routes", __name__)
s3 = S3Client()

ALLOWED_EXTENSIONS = {"txt", "pdf", "jpg", "png", "gif"}


@routes.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return (
        render_template(
            "upload.html", message="The file is too large. Maximum size is 3MB."
        ),
        413,
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@routes.route("/")
def index():
    return render_template("index.html")


# get para mostrar formulario para seleccionar archivo,
# post para enviar los datos al servidor, en este caso para subir
@routes.route("/upload", methods=["GET", "POST"])
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
                bucket = current_app.config["DEFAULT_BUCKET"]
                s3.upload_fileobj(fileobj=f, Bucket=bucket, Key=unique_name)
                message = f"File uploaded and saved: {unique_name}"
                return render_template("upload.html", message=message)
        else:
            logging.warning("Attempted to upload without providing a file")
            return render_template("upload.html", message="Error: Object not uploaded")


@routes.route("/download")
def download():
    return "<p>Ruta para descargar objeto</p>"


@routes.route("/delete")
def delete():
    return "<p>Ruta para borrar objeto</p>"


@routes.route("/list")
def list_objects():
    return "<p>Ruta para listar objetos en un bucket</p>"


@routes.route("/list_buckets")
def list_buckets():
    return "<p>Ruta para listar buckets</p>"


@routes.route("/create_bucket")
def create_bucket():
    return "<p>Ruta para crear bucket</p>"
