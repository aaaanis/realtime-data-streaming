variable "snowflake_account"     { type = string }
variable "snowflake_user"        { type = string }
variable "snowflake_password"    { type = string; sensitive = true }
variable "snowflake_role"        { type = string; default = "ACCOUNTADMIN" }

variable "confluent_api_key"     { type = string; sensitive = true }
variable "confluent_api_secret"  { type = string; sensitive = true }
variable "environment_id"        { type = string }   # Confluent Cloud env ID

variable "cloud_provider"        { type = string; default = "AWS" }
variable "region"                { type = string; default = "us-east-2" }
