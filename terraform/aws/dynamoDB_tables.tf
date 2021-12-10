# To apply just one table use the following:
# terraform plan/apply -target=module.dynamodb_table_play (example)

# For the rem feature
module "dynamodb_table" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "1.1.0"

  name                           = "remember"
  hash_key                       = "discord_server_id"
  range_key                      = "rem_key"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "discord_server_id"
      type = "N"
    },
    {
      name = "rem_key"
      type = "S"
    }
  ]

  tags = {
    managed_by = "terraform"
  }
}

# For the loud commands
module "dynamodb_table_loud" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "1.1.0"

  name                           = "loud"
  hash_key                       = "discord_server_id"
  range_key                      = "discord_handle"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "discord_server_id"
      type = "N"
    },
    {
      name = "discord_handle"
      type = "S"
    },
  ]

  tags = {
    managed_by = "terraform"
  }
}

# For the play commands
module "dynamodb_table_play" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "1.1.0"

  name                           = "play"
  hash_key                       = "discord_server_id"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "discord_server_id"
      type = "N"
    },
  ]

  tags = {
    managed_by = "terraform"
  }
}

# For the tts commands
module "dynamodb_table_tts" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "1.1.0"

  name                           = "tts"
  hash_key                       = "discord_server_id"
  range_key                      = "discord_handle"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "discord_server_id"
      type = "N"
    },
    {
      name = "discord_handle"
      type = "S"
    },
  ]

  tags = {
    managed_by = "terraform"
  }
}

# For the Sparkle commands
module "dynamodb_table_sparkle" {
  source  = "terraform-aws-modules/dynamodb-table/aws"
  version = "1.1.0"

  name                           = "sparkle"
  hash_key                       = "discord_server_id"
  range_key                      = "discord_handle"
  billing_mode                   = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "discord_server_id"
      type = "N"
    },
    {
      name = "discord_handle"
      type = "S"
    },
  ]

  tags = {
    managed_by = "terraform"
  }
}
