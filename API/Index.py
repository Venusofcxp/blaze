import time
import re
import requests

BASE_URL = "https://www.bestblaze.com.br"
DOUBLE_URL = BASE_URL + "/jogadasDouble"
CRASH_URL = BASE_URL + "/jogadasCrash"

UPDATE_INTERVAL = 1
TIMEOUT = 5

HEADERS = {"User-Agent": "Mozilla/5.0"}

session = requests.Session()
session.headers.update(HEADERS)

double_cache = {"data": [], "last": 0, "status": "init"}
crash_cache = {"data": [], "last": 0, "status": "init"}


def get_token():
    try:
        r = session.get(BASE_URL, timeout=TIMEOUT)
        match = re.search(r"_token:\s*'([^']+)'", r.text)
        if match:
            return match.group(1)
    except:
        pass
    return None


def update_double():
    now = time.time()

    if now - double_cache["last"] < UPDATE_INTERVAL:
        return

    token = get_token()
    if not token:
        double_cache["status"] = "token_error"
        return

    try:
        r = session.post(
            DOUBLE_URL,
            data={"ini": 1, "_token": token},
            timeout=TIMEOUT
        )

        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                double_cache["data"] = data
                double_cache["last"] = now
                double_cache["status"] = "ok"
        else:
            double_cache["status"] = f"http_{r.status_code}"

    except:
        double_cache["status"] = "error"


def update_crash():
    now = time.time()

    if now - crash_cache["last"] < UPDATE_INTERVAL:
        return

    token = get_token()
    if not token:
        crash_cache["status"] = "token_error"
        return

    try:
        r = session.post(
            CRASH_URL,
            data={"ini": 1, "_token": token},
            timeout=TIMEOUT
        )

        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                crash_cache["data"] = data
                crash_cache["last"] = now
                crash_cache["status"] = "ok"
        else:
            crash_cache["status"] = f"http_{r.status_code}"

    except:
        crash_cache["status"] = "error"


# ==============================
# ENTRYPOINT VERCEL
# ==============================
def handler(request):

    path = request.path

    if path.endswith("/double"):
        update_double()
        return {
            "source": "bestblaze",
            "updated_at": double_cache["last"],
            "status": double_cache["status"],
            "results": double_cache["data"],
        }

    if path.endswith("/crash"):
        update_crash()
        return {
            "source": "bestblaze",
            "updated_at": crash_cache["last"],
            "status": crash_cache["status"],
            "results": crash_cache["data"],
        }

    return {"server": "online"}
