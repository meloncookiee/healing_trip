import logging
from typing import Any

import requests

from config import CONCERT_API_KEY, CONCERT_BASE_URL

logger = logging.getLogger(__name__)


class ConcertApiError(Exception):
    pass


def fetch_concert_page(page_index: int = 1, page_size: int = 100) -> dict[str, Any]:
    if not CONCERT_API_KEY:
        raise ConcertApiError("CONCERT_API_KEY가 설정되지 않았습니다.")

    params = {
        "KEY": CONCERT_API_KEY,
        "Type": "json",
        "pIndex": page_index,
        "pSize": page_size,
    }
    try:
        response = requests.get(CONCERT_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.exception("경기도 공연/문화행사 API 호출 실패")
        raise ConcertApiError(f"경기도 공연 API 호출 실패: {exc}") from exc


def extract_concert_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    root = payload.get("Ggculturevent")
    if not isinstance(root, list) or not root:
        raise ConcertApiError("경기도 공연 API 응답 형식이 올바르지 않습니다.")

    total = 0
    rows: list[dict[str, Any]] = []
    for block in root:
        if not isinstance(block, dict):
            continue
        if "head" in block:
            for head_item in block["head"]:
                if not isinstance(head_item, dict):
                    continue
                if "list_total_count" in head_item:
                    total = int(head_item["list_total_count"])
                result = head_item.get("RESULT")
                if isinstance(result, dict):
                    code = str(result.get("CODE", ""))
                    if code and not code.startswith("INFO-0"):
                        message = result.get("MESSAGE", code)
                        raise ConcertApiError(f"경기도 공연 API 오류: {code} {message}")
        if "row" in block and isinstance(block["row"], list):
            rows.extend(item for item in block["row"] if isinstance(item, dict))
    return rows, total
