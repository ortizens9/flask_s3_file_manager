resource "aws_s3_bucket" "app_bucket" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Name        = "S3 File Manager Bucket"
    Environment = "Dev-Terraform"
  }
}
