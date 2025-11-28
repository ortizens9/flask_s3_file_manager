from app.s3_client import S3Client


def main():
    s3 = S3Client()
    bucket_name = "test-s3-proyecto-2025-daniel-ortiz-v2"
    objects = s3.list_objects(bucket_name)
    if not objects:
        print("No hay objectos que mostrar.")
    else:
        print(f"Objetos en el bucket ({len(objects)}):")
        for obj in objects:
            print("-", obj)


if __name__ == "__main__":
    main()
