import os
from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = os.environ.get(
        "S3_BUCKET_NAME", 
        "terraform-file-manager-default-s3bucket-daniel-2026"
    )

    object_name = "prueba.txt"
    
    download_path = "descarga_prueba.txt"
    success = s3.download_file(bucket_name, object_name, download_path)
    print(f"Archivo descargado: {success}")


if __name__ == "__main__":
    main()
