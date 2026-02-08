import time
import re
import requests

BASE_URL = "https://www.bestblaze.com.br"
CRASH_URL = BASE_URL + "/jogadasCrash"

UPDATE_INTERVAL = 1
TIMEOUT = 5

HEADERS = {"User-Agent": "Mozilla/5.0"}

session = requests.Session()
session.headers.update(HEADERS)

cache = {"data": [], "last": 0, "status": "init"}


def get_token():
    try:
        r = session.get(BASE_URL, timeout=TIMEOUT)
        match = re.search(r"_token:\s*'([^']+)'", r.text)
        if match:
            return match.group(1)
    except:
        pass
    return None


def handler(request):
    now = time.time()

    if now - cache["last"] >= UPDATE_INTERVAL:
        token = get_token()

        if token:
            try:
                r = session.post(
                    CRASH_URL,
                    data={"ini": 1, "_token": token},
                    timeout=TIMEOUT
                )

                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data:
                        cache["data"] = data
                        cache["last"] = now
                        cache["status"] = "ok"
                else:
                    cache["status"] = f"http_{r.status_code}"

            except:
                cache["status"] = "error"
        else:
            cache["status"] = "token_error"

    return {
        "source": "bestblaze",
        "updated_at": cache["last"],
        "status": cache["status"],
        "results": cache["data"],
    }
