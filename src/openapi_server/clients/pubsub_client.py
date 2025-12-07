from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()

PROJECT_ID = "matchmaking-services"
TOPIC = "matchmaking-events"

topic_path = publisher.topic_path(PROJECT_ID, TOPIC)

def publish_event(payload: dict):
    data = json.dumps(payload).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print("Published event ID:", future.result())
