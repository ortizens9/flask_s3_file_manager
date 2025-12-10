import boto3
import logging
from botocore.exceptions import ClientError
import os


class S3Error(Exception):
    """Errores generales de S3."""

    pass


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
            logging.error(f"Error al listar: {e}", exc_info=True)
            raise S3Error(f"No se pudieron listar los buckets") from e

    def create_bucket(self, bucket_name, region=None):
        if region == None:
            region = self.s3.meta.region_name
        try:
            if region == "us-east-1":
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
        except ClientError as e:
            logging.error(
                f"Error al crear bucket '{bucket_name}' en region '{region}': {e}",
                exc_info=True,
            )
            raise S3Error(f"No se pudo crear el bucket '{bucket_name}'") from e

    def upload_file(self, file_path, bucket_name, object_name=None):
        """Sube un archivo a un bucket S3."""
        # Si object_name no se proporciona, usa el nombre del archivo local.
        if object_name is None:
            object_name = os.path.basename(file_path)
        try:
            self.s3.upload_file(Filename=file_path, Bucket=bucket_name, Key=object_name)

        except ClientError as e:
            logging.error(
                f"Error al subir el archivo '{file_path}' a '{bucket_name}'/'{object_name}': {e}",
                exc_info=True,
            )
            raise S3Error(
                f"No se pudo subir el archivo '{file_path}' a '{bucket_name}'"
            ) from e

    def download_file(self, bucket_name, object_name, file_path):
        """Descarga un archivo del bucket"""
        try:
            self.s3.download_file(bucket_name, object_name, file_path)

        except ClientError as e:
            logging.error(
                f"Error al descargar el archivo '{object_name}' del bucket '{bucket_name}' : {e}",
                exc_info=True,
            )
            raise S3Error(
                f"No se pudo descargar el archivo '{object_name}' del bucket '{bucket_name}'"
            ) from e

    def delete_object(self, bucket_name, object_name):
        """Elimina un objeto del bucket S3."""
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=object_name)

        except ClientError as e:
            logging.error(
                f"Error al eliminar el archivo '{object_name}' del bucket '{bucket_name}': {e}",
                exc_info=True,
            )
            raise S3Error(
                f"No se pudo borrar el archivo '{object_name}' del bucket '{bucket_name}'"
            ) from e

    def list_objects(self, bucket_name):
        """Lista los objetos en un bucket S3."""
        try:
            paginator = self.s3.get_paginator("list_objects_v2")
            all_keys = []
            for page in paginator.paginate(Bucket=bucket_name):
                for obj in page.get("Contents", []):
                    all_keys.append(obj["Key"])
            return all_keys
        except ClientError as e:
            logging.error(
                f"Error al listar los objetos en el bucket '{bucket_name}': {e}"
            )
            raise S3Error(
                f"No se pueden listar los objetos en el bucket '{bucket_name}'"
            ) from e
