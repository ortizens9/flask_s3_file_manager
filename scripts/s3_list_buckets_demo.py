from app.s3_client import S3Client


def main():
    s3 = S3Client()
    buckets = s3.list_buckets()
    if not buckets:
        print("No hay buckets para mostrar.")
    else:
        print(f"Buckets encontrados ({len(buckets)}):")
        for bucket in buckets:
            print("-", bucket)


if __name__ == "__main__":
    main()
