#!/usr/bin/env python3
"""
Kafka producer emitting synthetic point‑of‑sale transactions.

Env vars
--------
KAFKA_BOOTSTRAP_SERVERS : host:port
KAFKA_SASL_USERNAME     : Confluent key
KAFKA_SASL_PASSWORD     : Confluent secret
KAFKA_TOPIC             : topic (default sales.transactions.events)
NUM_EVENTS              : messages to send (default 1000)
SLEEP_MS                : delay between messages (default 100)
"""

from __future__ import annotations
import os, time, random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from faker import Faker
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer, JSONSerializer

fake = Faker()

BOOTSTRAP = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
USERNAME  = os.environ["KAFKA_SASL_USERNAME"]
PASSWORD  = os.environ["KAFKA_SASL_PASSWORD"]
TOPIC     = os.getenv("KAFKA_TOPIC", "sales.transactions.events")
NUM       = int(os.getenv("NUM_EVENTS", "1000"))
SLEEP_MS  = int(os.getenv("SLEEP_MS", "100"))

@dataclass
class SalesEvent:
    transaction_id: str
    store_id: str
    product_id: str
    quantity: int
    unit_price: float
    total_amount: float
    payment_type: str
    transaction_ts_utc: str
    event_ts_utc: str

def generate_event() -> SalesEvent:
    qty  = random.randint(1, 10)
    price = round(random.uniform(2, 500), 2)
    amount = round(qty * price, 2)

    return SalesEvent(
        transaction_id=fake.uuid4(),
        store_id=fake.bothify(text="STORE_##"),
        product_id=fake.bothify(text="SKU_####"),
        quantity=qty,
        unit_price=price,
        total_amount=amount,
        payment_type=random.choice(["CREDIT_CARD", "CASH", "MOBILE_PAY", "LOYALTY"]),
        transaction_ts_utc=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        event_ts_utc=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
    )

def _serializer(obj, _ctx):
    return asdict(obj)

conf = {
    "bootstrap.servers": BOOTSTRAP,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": USERNAME,
    "sasl.password": PASSWORD,
    "key.serializer": StringSerializer("utf_8"),
    "value.serializer": JSONSerializer(_serializer),
}

producer = SerializingProducer(conf)

def delivery_report(err, msg):  # pragma: no cover
    if err:
        print(f"❌  delivery failed for key={msg.key()}: {err}")
    else:
        print(f"✅  {msg.topic()} [{msg.partition()}] offset {msg.offset()}")

def main() -> None:
    for _ in range(NUM):
        evt = generate_event()
        producer.produce(TOPIC, key=evt.transaction_id, value=evt, on_delivery=delivery_report)
        producer.poll(0)
        time.sleep(SLEEP_MS / 1000)
    producer.flush()

if __name__ == "__main__":
    main()
