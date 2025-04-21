terraform {
  required_version = ">= 1.6.0"
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = ">= 0.67.0"
    }
    confluent = {
      source  = "Mongey/confluentcloud"
      version = ">= 1.0.0"
    }
  }
}
