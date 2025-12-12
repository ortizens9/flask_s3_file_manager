from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = "file-manager-s3-bucket-default-daniel-ortiz"
    success = s3.create_bucket(bucket_name)
    print("Bucket creado:", success)


if __name__ == "__main__":
    main()
