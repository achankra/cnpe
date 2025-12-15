resource "aws_security_group" "web" {
  name        = "cnpe-demo-web"
  description = "Demo SG"
  vpc_id      = "vpc-xxxxxxxx" # for a pure demo you can leave this out only if you're not applying
}

resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

  monitoring = true

  #  often required to avoid "public IP" findings
  associate_public_ip_address = false

  vpc_security_group_ids = [aws_security_group.web.id]

  tags = {
    environment = "demo"
    owner       = "platform-team"
  }
}



