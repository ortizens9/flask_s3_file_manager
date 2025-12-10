from flask import Flask, request
import logging

app = Flask(__name__)


@app.route("/")
def index():
    return "<p>Página principal del Gestor S3</p>"


# get para mostrar formulario para seleccionar archivo,
# post para enviar los datos al servidor, en este caso para subir
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files.get("the_file")
        if f:
            return f"Archivo recibido: {f.filename}"
    else:
        logging.warning("Intento de subir archivo sin enviar archivo")
        return "Error: no se envió ningún archivo"


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
