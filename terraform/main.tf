############################################################
# Providers
############################################################
provider "snowflake" {
  account  = var.snowflake_account
  username = var.snowflake_user
  password = var.snowflake_password
  role     = var.snowflake_role
}

provider "confluent" {
  api_key    = var.confluent_api_key
  api_secret = var.confluent_api_secret
}

############################################################
# Snowflake objects
############################################################
resource "snowflake_database" "sales_analytics" { name = "SALES_ANALYTICS" }

resource "snowflake_schema" "raw" {
  name     = "RAW"
  database = snowflake_database.sales_analytics.name
}

resource "snowflake_warehouse" "stream_wh" {
  name                 = "STREAM_WH"
  warehouse_size       = "XSMALL"
  auto_suspend         = 60
  auto_resume          = true
  initially_suspended  = true
}

resource "snowflake_table" "transactions" {
  database = snowflake_database.sales_analytics.name
  schema   = snowflake_schema.raw.name
  name     = "SALES_TRANSACTIONS"

  column { name = "DATA" type = "VARIANT" }
  comment = "Inbound transactional payloads"
}

resource "snowflake_sql" "pipe" {
  warehouse = snowflake_warehouse.stream_wh.name
  sql = <<-SQL
    CREATE OR REPLACE STREAMING INGEST PIPE SALES_TRANSACTIONS_PIPE
      TABLE SALES_ANALYTICS.RAW.SALES_TRANSACTIONS
      ON_ERROR = CONTINUE;
  SQL
  depends_on = [snowflake_table.transactions]
}

resource "snowflake_sql" "schema_udf" {
  warehouse  = snowflake_warehouse.stream_wh.name
  sql        = file("${path.module}/udf.sql")
  depends_on = [snowflake_table.transactions]
}

############################################################
# Confluent Cloud (Kafka) objects
############################################################
resource "confluent_environment" "env" {
  id           = var.environment_id          # existing environment
  display_name = "sales-env"
}

resource "confluent_kafka_cluster" "cluster" {
  display_name = "sales-cluster"
  availability = "SINGLE_ZONE"
  cloud        = var.cloud_provider
  region       = var.region

  environment { id = confluent_environment.env.id }
  basic {}
}

resource "confluent_kafka_topic" "topic" {
  topic_name       = "sales.transactions.events"
  partitions_count = 3
  cluster          { id = confluent_kafka_cluster.cluster.id }
  config           = { "cleanup.policy" = "delete" }
}
