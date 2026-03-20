# EFS for persisting ChromaDB data across container restarts
resource "aws_efs_file_system" "chroma" {
  creation_token   = "${var.app_name}-chroma"
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"
  encrypted        = true

  tags = {
    Name        = "${var.app_name}-chroma-efs"
    Environment = var.environment
  }
}

resource "aws_efs_mount_target" "chroma" {
  count           = 2
  file_system_id  = aws_efs_file_system.chroma.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_access_point" "chroma" {
  file_system_id = aws_efs_file_system.chroma.id

  posix_user {
    gid = 1000
    uid = 1000
  }

  root_directory {
    path = "/chroma_db"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }

  tags = {
    Name        = "${var.app_name}-chroma-ap"
    Environment = var.environment
  }
}
