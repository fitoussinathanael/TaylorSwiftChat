import uuid
from datetime import datetime

PATIENT_DB = {}


def create_patient(text: str):
    pid = str(uuid.uuid4())[:8]

    PATIENT_DB[pid] = {
        "id": pid,
        "created_at": datetime.now().isoformat(),
        "events": [text],
        "last_flow": None,
        "last_assist": None
    }

    return pid


def get_patient(pid):
    return PATIENT_DB.get(pid)


def update_patient(pid, text, flow=None, assist=None):

    if pid not in PATIENT_DB:
        return None

    PATIENT_DB[pid]["events"].append(text)

    # garder seulement les 5 derniers événements (anti overload)
    PATIENT_DB[pid]["events"] = PATIENT_DB[pid]["events"][-5:]

    if flow:
        PATIENT_DB[pid]["last_flow"] = flow

    if assist:
        PATIENT_DB[pid]["last_assist"] = assist

    return PATIENT_DB[pid]
