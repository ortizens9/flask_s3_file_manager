from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = "test-s3-manager-daniel-ortiz-2025"
    object_name = "prueba.txt"
    download_path = "descarga_prueba.txt"
    success = s3.download_file(bucket_name, object_name, download_path)
    print(f"Archivo descargado: {success}")


if __name__ == "__main__":
    main()
