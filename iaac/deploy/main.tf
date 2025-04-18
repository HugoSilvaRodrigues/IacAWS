provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "s3_bucket" {
  bucket = "s3-273354626311"

  tags = {
    Name        = "Projeto IAAC"
    Environment = "DEV"
  }

  provisioner "local-exec" {
    command = "${path.module}/upload_to_s3.sh"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "aws s3 rm s3://s3-273354626311 --recursive"
  }
}

resource "aws_instance" "api" {
  ami                  = "ami-08b5b3a93ed654d19"
  instance_type        = "t2.micro"
  iam_instance_profile = aws_iam_instance_profile.ec2_s3_profile.name
  vpc_security_group_ids = [aws_security_group.ml_api.id]

  user_data = <<-EOF
                #!/bin/bash
                sudo yum update -y
                sudo yum install -y python3 python3-pip 
                sudo pip3 install \
                python-dateutil==2.8.2 \
                fastapi==0.109.0 \
                pydantic==2.10.5 \
                joblib==1.2.0 \
                uvicorn==0.29.0 \
                pandas==2.1.4 \
                scikit-learn==1.5.2 \
                numpy==1.26.4 \
                scipy==1.11.1 \
                gunicorn==21.2.0
                sudo mkdir /ml_app
                sudo rm -rf /usr/bin/aws 
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install --update
                sudo aws s3 sync s3://s3-273354626311 /ml_app
                cd /ml_app
                nohup python3 api.py &
              EOF

  tags = {
    Name = "Api"
  }
}

resource "aws_security_group" "ml_api" {
  name        = "ml_api"
  description = "Security Group for API running in EC2"
}

resource "aws_security_group_rule" "permite_http" {
  type              = "ingress"
  security_group_id = aws_security_group.ml_api.id
  from_port         = 8080
  to_port           = 8080
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "permite_ssh" {
  type              = "ingress"
  security_group_id = aws_security_group.ml_api.id
  from_port         = 22
  to_port           = 22
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "permite_conexao" {
  type              = "egress"
  security_group_id = aws_security_group.ml_api.id
  from_port         = 0
  to_port           = 65535
  protocol         = "-1"
  cidr_blocks      = ["0.0.0.0/0"]
}

resource "aws_iam_role" "ec2_s3_role_access" {
  name = "ec2_s3_role_access"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "s3_access_policy" {
  name = "s3_access_policy"
  role = aws_iam_role.ec2_s3_role_access.name
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      Effect = "Allow",
      Resource = [
        "${aws_s3_bucket.s3_bucket.arn}/*",
        "${aws_s3_bucket.s3_bucket.arn}"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_s3_profile" {
  name = "ec2_s3_profile"
  role = aws_iam_role.ec2_s3_role_access.name
}
