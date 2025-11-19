import requests

DONOR_REGISTRY_BASE_URL = "https://donor-registry-service-730071231868.us-central1.run.app"

def get_health():
    url = f"{DONOR_REGISTRY_BASE_URL}/health"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def list_donors():
    url = f"{DONOR_REGISTRY_BASE_URL}/donors"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_donor(donor_id: str):
    url = f"{DONOR_REGISTRY_BASE_URL}/donors/{donor_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def list_organs_for_donor(donor_id: str):
    url = f"{DONOR_REGISTRY_BASE_URL}/donors/{donor_id}/organs"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
