# Terraform IaC Security Test Fixture
# Remediated infrastructure configurations

resource "aws_s3_bucket" "vulnerable_public_bucket" {
  bucket = "my-vulnerable-test-bucket-public-read"
}

# Remediated: S3 Bucket ACL set to private
resource "aws_s3_bucket_acl" "vulnerable_bucket_acl" {
  bucket = aws_s3_bucket.vulnerable_public_bucket.id
  acl    = "private"
}

# Remediated: Block all public access to S3 bucket
resource "aws_s3_bucket_public_access_block" "vulnerable_bucket_public_block" {
  bucket = aws_s3_bucket.vulnerable_public_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Remediated: Security group allowing restricted SSH access (10.0.0.0/16)
resource "aws_security_group" "unrestricted_ssh_sg" {
  name        = "unrestricted-ssh-sg"
  description = "Security group with restricted SSH ingress"
  vpc_id      = "vpc-12345678"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Remediated: Encrypted EBS volume
resource "aws_ebs_volume" "unencrypted_volume" {
  availability_zone = "us-east-1a"
  size              = 20
  encrypted         = true

  tags = {
    Name = "unencrypted-ebs-test"
  }
}
