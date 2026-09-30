import os
from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = os.environ.get(
        "S3_BUCKET_NAME", 
        "terraform-file-manager-default-s3bucket-daniel-2026"
    )
    
    objects = s3.list_objects(bucket_name)
    if not objects:
        print("No hay objectos que mostrar.")
    else:
        print(f"Objetos en el bucket ({len(objects)}):")
        for obj in objects:
            print("-", obj)


if __name__ == "__main__":
    main()
