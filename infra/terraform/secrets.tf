resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${var.app_name}/openai-api-key"
  description             = "OpenAI API key for rag-api"
  recovery_window_in_days = 7

  tags = {
    Name        = "${var.app_name}-openai-key"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}
