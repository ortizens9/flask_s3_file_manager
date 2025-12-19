from flask import Blueprint, render_template, request, current_app, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from s3_service import download_file, upload_file, S3ServiceError
import os

routes = Blueprint("routes", __name__)

# HTTP, depende de Flask


@routes.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return (
        render_template(
            "upload.html", message="The file is too large. Maximum size is 3MB."
        ),
        413,
    )


@routes.route("/")
def index():
    return render_template("index.html")


# get para mostrar formulario para seleccionar archivo,
# post para enviar los datos al servidor, en este caso para subir
@routes.route("/upload", methods=["GET", "POST"])
def upload():
    bucket = current_app.config["DEFAULT_BUCKET"]
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        f = request.files.get("the_file")
        if f and f.filename != "":
            try:
                unique_name = upload_file(f, bucket)
                return render_template(
                    "upload.html", message=f"File uploaded successfully: {unique_name}"
                )
            except S3ServiceError as e:
                return render_template("upload.html", message=str(e))
        else:
            return render_template("upload.html", message="Error: Object not uploaded")


@routes.route("/download/<object_name>")
def download(object_name):
    bucket = current_app.config["DEFAULT_BUCKET"]
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", object_name)
    # Para pulir necesitamos crear una función para borrar los archivos temporales.
    try:
        download_file(bucket, object_name, file_path)
        return send_file(file_path, as_attachment=True)
    except S3ServiceError as e:
        return render_template("download.html", message=str(e))


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
