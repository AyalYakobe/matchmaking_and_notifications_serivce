from fastapi import APIRouter
import requests

from openapi_server.clients.ms1_client import MS1Client
from openapi_server.clients.ms2_client import MS2Client

router = APIRouter()

# Shared base URL for MS1 + MS2
COMPOSITE_BASE = "https://composite-service-730071231868.us-central1.run.app"

ms1 = MS1Client(COMPOSITE_BASE)
ms2 = MS2Client(COMPOSITE_BASE)


# ===============================================================
# MS1: Donor Registry
# ===============================================================
@router.get("/ms1/health", tags=["Composite"])
def ms1_health():
    return ms1.list_donors()


@router.get("/ms1/donors", tags=["Composite"])
def ms1_list_donors():
    return ms1.list_donors()


@router.get("/ms1/donors/{donor_id}", tags=["Composite"])
def ms1_get_donor(donor_id: str):
    return ms1.get_donor(donor_id)


@router.get("/ms1/donors/{donor_id}/organs", tags=["Composite"])
def ms1_organs_for_donor(donor_id: str):
    return ms1.list_organs_for_donor(donor_id)


@router.get("/ms1/organs", tags=["Composite"])
def ms1_list_organs():
    return ms1.list_organs()


@router.get("/ms1/consents", tags=["Composite"])
def ms1_list_consents():
    return ms1.list_consents()


@router.get("/ms1/consents/{consent_id}", tags=["Composite"])
def ms1_get_consent(consent_id: str):
    return ms1.get_consent(consent_id)


@router.get("/ms1/all", tags=["Composite"])
def ms1_all():
    return {
        "donors": ms1.list_donors(),
        "organs": ms1.list_organs(),
        "consents": ms1.list_consents(),
    }


# ---------- NEW: DELETE organ ----------
@router.delete("/ms1/organs/{organ_id}", tags=["Composite"])
def ms1_delete_organ(organ_id: str):
    return ms1.delete_organ(organ_id)



# ===============================================================
# MS2: Recipient Registry
# ===============================================================
@router.get("/ms2/recipients", tags=["Composite"])
def ms2_list_recipients():
    return ms2.list_recipients()


@router.get("/ms2/recipients/{recipient_id}", tags=["Composite"])
def ms2_get_recipient(recipient_id: str):
    return ms2.get_recipient(recipient_id)


@router.get("/ms2/recipients/{recipient_id}/needs", tags=["Composite"])
def ms2_needs_for_recipient(recipient_id: str):
    return ms2.list_needs_for_recipient(recipient_id)


@router.get("/ms2/needs", tags=["Composite"])
def ms2_list_needs():
    return ms2.list_needs()


@router.get("/ms2/needs/{need_id}", tags=["Composite"])
def ms2_get_need(need_id: str):
    return ms2.get_need(need_id)


@router.get("/ms2/hospitals", tags=["Composite"])
def ms2_list_hospitals():
    return ms2.list_hospitals()


@router.get("/ms2/hospitals/{hospital_id}", tags=["Composite"])
def ms2_get_hospital(hospital_id: str):
    return ms2.get_hospital(hospital_id)


@router.get("/ms2/all", tags=["Composite"])
def ms2_all():
    return {
        "recipients": ms2.list_recipients(),
        "needs": ms2.list_needs(),
        "hospitals": ms2.list_hospitals(),
    }


# ---------- NEW: DELETE need ----------
@router.delete("/ms2/needs/{need_id}", tags=["Composite"])
def ms2_delete_need(need_id: str):
    return ms2.delete_need(need_id)



# ===============================================================
# COMPOSITE SNAPSHOT
# ===============================================================
@router.get("/aggregate/full-snapshot", tags=["Composite"])
def aggregate_full_snapshot():
    r = requests.get(f"{COMPOSITE_BASE}/snapshot/inventory")
    r.raise_for_status()
    return r.json()
