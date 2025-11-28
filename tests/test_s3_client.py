import os
import pytest
from moto.s3 import mock_s3
from app.s3_client import S3Client


@pytest.fixture
def s3_client():
    with mock_s3():
        client = S3Client(region_name="eu-west-1")
        client.create_bucket("bucket-prueba")
        yield client


def test_list_buckets(s3_client):
    buckets = s3_client.list_buckets()
    assert "bucket-prueba" in buckets


def test_create_bucket(s3_client):
    bucket_name = "nuevo-bucket"
    s3_client.create_bucket(bucket_name)
    buckets = s3_client.list_buckets()
    assert "nuevo-bucket" in buckets


def test_upload_file(s3_client, tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello World!")
    s3_client.upload_file(file_path, "bucket-prueba")
    objects = s3_client.list_objects("bucket-prueba")
    assert "test_file.txt" in objects


def test_download_file(s3_client, tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello World!")
    s3_client.upload_file(file_path, "bucket-prueba")
    download_path = tmp_path / "test_file_downloaded.txt"
    s3_client.download_file("bucket-prueba", "test_file.txt", download_path)
    assert download_path.exists()
    assert download_path.read_text() == "Hello World!"


def test_delete_object(s3_client, tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello World!")
    s3_client.upload_file(file_path, "bucket-prueba")
    s3_client.delete_object("bucket-prueba", "test_file.txt")
    objects = s3_client.list_objects("bucket-prueba")
    assert "test_file.txt" not in objects
