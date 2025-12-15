#  Correct resource type
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}


provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "data" {
  bucket = "cnpe-demo-data"

  tags = {
    environment = "demo"
    owner       = "platform-team"
  }
}

# Block all public access at the bucket level (best-practice + Trivy-friendly)
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

# Default encryption (SSE-S3). Use aws:kms if you want a “stronger” posture.
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Optional but commonly recommended
resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}


