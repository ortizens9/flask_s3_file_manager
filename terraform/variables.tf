variable "aws_region" {
  description = "Región de AWS donde desplegaremos los recursos"
  type        = string
  default     = "eu-west-1"
}

variable "bucket_name" {
  description = "Nombre único para el bucket S3 de Terraform"
  type        = string
  default     = "terraform-file-manager-default-s3bucket-daniel-2026"
}
