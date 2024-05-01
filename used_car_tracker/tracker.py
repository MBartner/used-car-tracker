import json
import logging
import time
from hashlib import sha256
from urllib.parse import unquote_plus, urlencode
from pathlib import Path

import httpx

DEDUP_SITES = "te|cm|cs|cv|eb|tc|ot|fbm|st"
RESULTS_KEY = "results"

logger = logging.getLogger()


def hash_params(search_params: bytes) -> str:
    m = sha256()
    m.update(search_params)
    return m.hexdigest()


def stringify_params(search_params: dict[str, str]) -> str:
    return unquote_plus(urlencode(search_params))


def get_token(search_params: dict[str, str], nonce: str) -> str:
    content = stringify_params(search_params)
    content += nonce
    token = hash_params(content.encode("utf-8"))
    return token


def get_results(log_dir: Path):
    for site in DEDUP_SITES.split("|"):
        params = {
            "make": "subaru",
            "model": "legacy",
            "minyear": "2020",
            "maxyear": "2020",
            "radius": "300",
            "originalradius": "300",
            "trim_kw": "Touring XT",
            "zip": "07307",
            "sort": "best_match",
            "sites": site,
            "deduplicationSites": DEDUP_SITES,
            "rpp": "50",
            "page": "1",
        }
        params["token"] = get_token(params, "d8007486d73c168684860aae427ea1f9d74e502b06d94609691f5f4f2704a07f")
        resp = httpx.get(
            "https://www.autotempest.com/queue-results",
            params=params,
        )
        if resp.status_code != 200:
            logger.warn("received status %d: %s", resp.status_code, resp.reason_phrase, extra=params)
            continue
        try:
            parsed = json.loads(resp.text)
        except Exception:
            logger.warn("failed to parse response data", extra=params)
            continue
        if RESULTS_KEY not in parsed:
            continue
        for result in parsed[RESULTS_KEY]:
            file_name = Path(f"result_{time.time_ns()}.json")
            log_path = log_dir / Path(file_name)
            with open(log_path, "w", encoding="utf-8") as file:
                json.dump(result, file)
