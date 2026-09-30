terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version =">= 1.0.0"
}

#La región se leerá en el archivo de variables.

provider "aws"{
  region =var.aws_region
}
