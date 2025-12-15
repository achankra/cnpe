# 1) Wrong resource type (validate should catch)
resource "aws_ec2_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

# 2) Misconfig / security issue (trivy should catch)
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
  acl    = "public-read"
}

# 3) Best-practice/provider rule issue (tflint should catch)
resource "aws_instance" "web2" {
  ami           = "ami-12345678"
  instance_type = "t3.super" # not real
}
