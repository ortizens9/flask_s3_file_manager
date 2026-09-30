import os
from flask import Flask
from .routes import routes

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024  # 3MB max file size
    
    # Registrar blueprint
    app.register_blueprint(routes)
    
    # Carga el bucket desde las variables de entorno (.env)
    # Si no existe la variable, usa el bucket de Terraform por defecto
    app.config["DEFAULT_BUCKET"] = os.environ.get(
        "S3_BUCKET_NAME", 
        "terraform-file-manager-default-s3bucket-daniel-2026"
    )
    
    return app