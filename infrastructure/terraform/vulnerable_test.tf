# Terraform IaC Security Test Fixture
# Demonstrates common infrastructure misconfigurations for IaC scanners

resource "aws_s3_bucket" "vulnerable_public_bucket" {
  bucket = "my-vulnerable-test-bucket-public-read"
}

# Vulnerable: S3 Bucket ACL set to public-read-write
resource "aws_s3_bucket_acl" "vulnerable_bucket_acl" {
  bucket = aws_s3_bucket.vulnerable_public_bucket.id
  acl    = "public-read-write"
}

# Vulnerable: Security group allowing unrestricted SSH access (0.0.0.0/0)
resource "aws_security_group" "unrestricted_ssh_sg" {
  name        = "unrestricted-ssh-sg"
  description = "Security group with open SSH ingress"
  vpc_id      = "vpc-12345678"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Vulnerable: Unencrypted EBS volume
resource "aws_ebs_volume" "unencrypted_volume" {
  availability_zone = "us-east-1a"
  size              = 20
  encrypted         = false

  tags = {
    Name = "unencrypted-ebs-test"
  }
}
