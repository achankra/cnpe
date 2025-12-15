#  Correct resource type
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

#  Secure-by-default storage
resource "aws_s3_bucket" "data" {
  bucket = "cnpe-demo-data"

  tags = {
    environment = "demo"
    owner       = "platform-team"
  }
}

