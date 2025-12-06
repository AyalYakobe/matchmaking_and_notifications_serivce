import base64
import json

def handle_event(event, context):
    print("Cloud Function triggered!")

    if "data" not in event:
        print("No data provided in event")
        return

    decoded = base64.b64decode(event.get("data")).decode("utf-8")
    data = json.loads(decoded)

    print("Received event:", data)
