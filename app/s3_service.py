from .s3_client import S3Client
import logging
import uuid
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"txt", "pdf", "jpg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class S3ServiceError(Exception):
    pass


# lógica negocio, no depende de Flask


def upload_file(fileobj, bucket_name):
    filename = fileobj.filename
    if not allowed_file(filename):
        raise S3ServiceError("Object format not allowed")
    secure_name = secure_filename(filename)
    unique_name = f"{uuid.uuid4().hex}_{secure_name}"
    s3 = S3Client()
    try:
        s3.upload_fileobj(fileobj=fileobj, Bucket=bucket_name, Key=unique_name)
    except Exception as e:
        logging.error("Error uploading file to S3", exc_info=True)
        raise S3ServiceError(f"Failed to upload file") from e

    return unique_name


def download_file(bucket_name, object_name, file_path):
    s3 = S3Client()
    try:
        s3.download_file(bucket_name, object_name, file_path)
    except Exception as e:
        logging.error("Error downloading file from S3", exc_info=True)
        raise S3ServiceError(f"Failed to download file") from e


def list_files(bucket_name):
    s3 = S3Client()
    try:
        objects = s3.list_objects(bucket_name)
        return objects
    except Exception as e:
        logging.error("Error listing the objects", exc_info=True)
        raise S3ServiceError(f"Failed listing objects") from e


def list_s3buckets():
    s3 = S3Client()
    try:
        buckets = s3.list_buckets()
        return buckets
    except Exception as e:
        logging.error("Error listing buckets", exc_info=True)
        raise S3ServiceError(f"Failed listing buckets") from e


def delete_file(bucket_name, object_name):
    s3 = S3Client()
    try:
        s3.delete_object(bucket_name, object_name)
    except Exception as e:
        logging.error("Error deleting object", exc_info=True)
        raise S3ServiceError(f"Failed deleting object") from e
