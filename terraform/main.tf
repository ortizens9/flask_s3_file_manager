resource "aws_s3_bucket" "app_bucket" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Name        = "S3 File Manager Bucket"
    Environment = "Dev-Terraform"
  }
}

resource "aws_iam_policy" "s3_app_policy" {
  name        = "flask-s3-app-policy"
  description = "Permisos S3 para el gestor S3"

  policy = jsonencode({
    Version= "2012-10-17",
    Statement= [
      {
        Sid= "Statement1"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ],
        Resource= aws_s3_bucket.app_bucket.arn
      },
      {
        Sid= "Statement2"
        Effect = "Allow"
        Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
        ],
        Resource= "${aws_s3_bucket.app_bucket.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_role"{
  name = "ecs-task-role-s3-flask"
  description = "Rol de ejecución del contenedor"
  
  assume_role_policy = jsonencode({
    Version= "2012-10-17"
    Statement= [
      {
        Sid= ""
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_s3_attach"{
  role = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.s3_app_policy.arn
}

resource "aws_iam_role" "ecs_exec_role"{
  name = "ecs-exec-role-flask-ecs"
  description = "Permisos a ECS desde fuera del contenedor"

  assume_role_policy = jsonencode({
    Version= "2012-10-17"
    Statement= [
     {
       Sid= ""
       Effect = "Allow"
       Principal = {
         Service = "ecs-tasks.amazonaws.com"
       }
       Action = "sts:AssumeRole"
     }
   ]
  })
}

resource "aws_iam_role_policy_attachment" "exec_role_policy_attach" {
  role = aws_iam_role.ecs_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecr_repository" "flask_s3_file_manager" {
  name                 = "flask-s3-file-manager"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push       = true
   }
}

resource "aws_ecs_cluster" "main" {
  name = "flask-app-cluster"
}

resource "aws_ecs_task_definition" "file_manager" {
  family                 = "flask-s3-task"
  requires_compatibilities = ["FARGATE"]
  network_mode           = "awsvpc"
  cpu                    = "256"
  memory                 = "512"

  execution_role_arn     = aws_iam_role.ecs_exec_role.arn
  task_role_arn          = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name = "flask-app"
      image = "${aws_ecr_repository.flask_s3_file_manager.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
     ]
   }
 ])
}

#La VPC de mi cuenta AWS por defecto
data "aws_vpc" "default" {
  default = true
}

#Las subredes de esa VPC
data "aws_subnets" "default" {
  filter {
    name = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

filter {
    name   = "map-public-ip-on-launch"
    values = ["true"]
  }
}

resource "aws_security_group" "flask_ecs_sg"{
  name   = "flask-ecs-sg"
  vpc_id = data.aws_vpc.default.id
  ingress  {
    from_port = 5000
    to_port = 5000
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress  {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_service" "flask_service" {
  name            = "flask-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.file_manager.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets = data.aws_subnets.default.ids
    security_groups = [aws_security_group.flask_ecs_sg.id]
    assign_public_ip = true
  }
}

output "s3_file_manager_url" {
  description = "URL del repositorio del gestor de S3"
  value = aws_ecr_repository.flask_s3_file_manager.repository_url
}
