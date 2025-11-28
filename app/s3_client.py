import boto3
from botocore.exceptions import ClientError
import os


class S3Client:
    """Cliente de alto nivel para operar con S3."""

    def __init__(self, region_name="eu-west-1"):
        self.s3 = boto3.client("s3", region_name=region_name)

    def list_buckets(self):
        """Lista los buckets de una cuenta en S3."""
        try:
            response = self.s3.list_buckets()
            bucket_names = [bucket["Name"] for bucket in response["Buckets"]]
            return bucket_names
        except ClientError as e:
            print(f"Error al listar: {e} ")
            return []

    def create_bucket(self, bucket_name):
        try:
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": self.s3.meta.region_name
                },
            )
            return True
        except ClientError as e:
            print(f"Error al crear bucket: {e} ")
            return False

    # TODO: añadir parámetro opcional 'region' para poder crear buckets
    # en otra región que no sea la configurada en self.s3, y manejar
    # la excepción IllegalLocationConstraintException si la región no coincide.
    # Desde aquí import os.
    def upload_file(self, file_path, bucket_name, object_name=None):
        """Sube un archivo a un bucket S3."""
        # Si object_name no se proporciona, usa el nombre del archivo local.
        if object_name is None:
            object_name = os.path.basename(file_path)
        try:
            self.s3.upload_file(Filename=file_path, Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(
                f"Error al subir el archivo {file_path} a {bucket_name}/{object_name}): {e} "
            )
            return False

    def download_file(self, bucket_name, object_name, file_path):
        """Descarga un archivo del bucket"""
        try:
            self.s3.download_file(bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            print(f"Error al descargar el archivo {object_name}: {e}")
            return False

    def delete_object(self, bucket_name, object_name):
        """Elimina un objeto del bucket S3."""
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Error al eliminar el archivo {object_name}: {e}")
            return False

    def list_objects(self, bucket_name):
        """Lista los objetos en un bucket S3."""
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            object_names = [object["Key"] for object in response.get("Contents", [])]
            return object_names
        except ClientError as e:
            return []
