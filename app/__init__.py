from flask import Flask, request, render_template
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)


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
            path = "uploads/" + secure_name
            f.save(path)
            message = f"File uploaded and saved: {secure_name}"
            return render_template("upload.html", message=message)
        else:
            logging.warning("Attempted to upload without providing a file")
            return "Error: Object not uploaded"


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
