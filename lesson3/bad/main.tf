# WRONG resource type (terraform validate will fail)
resource "aws_ec2_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

#  Public data exposure (trivy config will flag)
resource "aws_s3_bucket" "data" {
  bucket = "cnpe-demo-data"
  acl    = "public-read"
}

#  Invalid instance type (tflint/provider rules)
resource "aws_instance" "broken" {
  ami           = "ami-12345678"
  instance_type = "t3.super"
}

