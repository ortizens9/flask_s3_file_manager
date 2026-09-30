import os
from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = os.environ.get(
        "S3_BUCKET_NAME", 
        "terraform-file-manager-default-s3bucket-daniel-2026"
    )

    object_name = "prueba.txt"
    
    success = s3.delete_object(bucket_name, object_name)
    print(f"Archivo eliminado: ", {success})


if __name__ == "__main__":
    main()
