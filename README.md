# Real‑Time Sales‑Transaction Streaming (Snowflake + Kafka)

Production pipeline that captures point‑of‑sale transactions from Kafka and lands them in Snowflake with sub‑5 second latency.  
Includes automatic schema evolution, latency SLO enforcement, and full IaC + CI/CD.

| Capability | Tech stack |
|------------|------------|
| Event transport | Kafka |
| Low‑latency ingest | **Snowpipe Streaming** |
| Automatic schema evolution | Snowpark Python UDF |
| Infrastructure as Code | Terraform |
| SLO monitoring & pipeline tests | PyTest (+ GitHub Actions) |

### Quick start

```bash
# 1 – Provision infrastructure
cd terraform
terraform init
terraform apply -var="..."      # supply secrets via TF_VARs or .tfvars

# 2 – Publish synthetic transactions
export KAFKA_BOOTSTRAP_SERVERS=$(terraform output -raw bootstrap_servers)
export KAFKA_SASL_USERNAME=...
export KAFKA_SASL_PASSWORD=...
python ../producer/producer.py

# 3 – Verify arrivals
snowsql -q "SELECT * FROM SALES_ANALYTICS.RAW.SALES_TRANSACTIONS LIMIT 10;"
