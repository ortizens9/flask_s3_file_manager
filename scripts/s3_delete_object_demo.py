from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = "test-s3-manager-daniel-ortiz-2025"
    object_name = "prueba.txt"
    success = s3.delete_object(bucket_name, object_name)
    print(f"Archivo eliminado: ", {success})


if __name__ == "__main__":
    main()
