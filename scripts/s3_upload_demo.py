from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = "test-s3-manager-daniel-ortiz-2025"
    success = s3.create_bucket(bucket_name)
    print("Bucket creado:", success)
    file_path = "prueba.txt"
    success2 = s3.upload_file(file_path, bucket_name)
    print("Archivo subido: ", success2)


if __name__ == "__main__":
    main()
