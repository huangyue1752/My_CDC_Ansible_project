from confluent_kafka import Consumer, KafkaException
from azure.eventhub import EventHubProducerClient,EventData
import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

def must_env(k:str)->str:
    v=os.getenv(k)
    if not v:
        raise RuntimeError(f"Missing required env var: {k}")
    return v
#===azure Auth (Service Principal)===
tenant_id=must_env("AZURE_TENANT_ID")
client_id=must_env("AZURE_CLIENT_ID")
client_secret=must_env("AZURE_CLIENT_SECRET")

key_vault_url = must_env("KEY_VAULT_URL")
kv_secret_name = must_env("KV_SECRET_NAME")
eventhub_name = must_env("EVENTHUB_NAME")

#Auth to Azure (service principal) via env vars you already have set
cred=ClientSecretCredential(
    tenant_id,
    client_id,
    client_secret
)

kv=SecretClient(vault_url=key_vault_url,credential=cred)
EHNS_CONN_STR=kv.get_secret(kv_secret_name).value


#=====CONFIG: Kafka (source)=====
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:29092")  # ✅ no space
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "mysql9_full.school.students")
KAFKA_GROUP = os.getenv("KAFKA_GROUP", "bridge-to-eventhub")
AUTO_OFFSET_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")


#===== CONFIG: Event Hubs (dest)=====

producer=EventHubProducerClient.from_connection_string(
    conn_str=EHNS_CONN_STR,
    eventhub_name=eventhub_name
)

consumer=Consumer({
    "bootstrap.servers":KAFKA_BOOTSTRAP,
    "group.id": KAFKA_GROUP,
    "auto.offset.reset": AUTO_OFFSET_RESET,
    "enable.auto.commit": False,
})

consumer.subscribe([KAFKA_TOPIC])

def send_to_eventhub(payload: bytes, props: dict):
    event= EventData(payload)
    event.properties=props
    producer.send_batch([event])


try:
    while True:
        msg=consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        
        payload=msg.value()

        props={
            "kafka_topic":msg.topic(),
            "kafka_partition": str(msg.partition()),
            "kafka_offset":str(msg.offset()),
        }

        # 1) write to EH
        send_to_eventhub(payload,props)

        # 2) commit for Kafka offset after writting successfully
        consumer.commit(message=msg, asynchronous=False)
except KeyboardInterrupt:
    print("Stopping bridge...")
finally:
    consumer.close()
    producer.close()