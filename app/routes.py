from flask import Blueprint, render_template, request, current_app, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from .s3_service import (
    download_file,
    upload_file,
    S3ServiceError,
    list_files,
    list_s3buckets,
    delete_file,
    new_bucket,
)
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


@routes.route("/download")
def download_wlink():
    bucket = current_app.config["DEFAULT_BUCKET"]
    try:
        objects = list_files(bucket)
        return render_template("download_wlink.html", objects=objects)
    except Exception as e:
        return f"Error: {e}"


@routes.route("/download/<object_name>")
def download(object_name):
    bucket = current_app.config["DEFAULT_BUCKET"]
    downloads_folder = os.path.join(current_app.root_path, "downloads")
    os.makedirs(downloads_folder, exist_ok=True)
    file_path = os.path.join(downloads_folder, object_name)
    # Para pulir necesitamos crear una función para borrar los archivos temporales.
    try:
        download_file(bucket, object_name, file_path)
        return send_file(file_path, as_attachment=True)
    except S3ServiceError as e:
        return f"Error: {str(e)}", 500


@routes.route("/delete", methods=["GET", "POST"])
def delete():
    bucket = current_app.config["DEFAULT_BUCKET"]
    objects = list_files(bucket)
    if request.method == "GET":
        return render_template("delete_file.html", objects=objects)
    elif request.method == "POST":
        obj_to_delete = request.form.get("object_name")
        if obj_to_delete in objects:
            try:
                delete_file(bucket, obj_to_delete)
                objects = list_files(bucket)
                return render_template(
                    "delete_file.html",
                    message=f"Object '{obj_to_delete}' deleted successfully",
                    objects=objects,
                )
            except S3ServiceError as e:
                return render_template(
                    "delete_file.html", message=str(e), objects=objects
                )
        else:
            return render_template(
                "delete_file.html",
                message=f"Object '{obj_to_delete}' not found in bucket.",
                objects=objects,
            )


@routes.route("/list")
def list_objects():
    bucket = current_app.config["DEFAULT_BUCKET"]
    objects = list_files(bucket)
    return render_template("list_objects.html", objects=objects)


@routes.route("/list_buckets")
def show_buckets():
    buckets = list_s3buckets()
    return render_template("list_buckets.html", buckets=buckets)


@routes.route("/create_bucket", methods=["GET", "POST"])
def create_bucket():
    buckets = list_s3buckets()
    if request.method == "GET":
        return render_template("create_bucket.html", buckets=buckets)
    elif request.method == "POST":
        nbucket_name = request.form.get("bucket_name")
        if nbucket_name != "":
            try:
                new_bucket(nbucket_name)
                buckets = list_s3buckets()
                return render_template(
                    "create_bucket.html",
                    message=f"Bucket {nbucket_name} created succesfully.",
                    buckets=buckets,
                )
            except S3ServiceError as e:
                return render_template(
                    "create_bucket.html", message=str(e), buckets=buckets
                )
        else:
            return render_template(
                "create_bucket.html",
                message="Error creating new bucket.",
                buckets=buckets,
            )
