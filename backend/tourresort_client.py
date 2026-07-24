import logging
from typing import Any

import requests

from config import TOURRESORT_API_KEY, TOURRESORT_BASE_URL

logger = logging.getLogger(__name__)


class TourResortApiError(Exception):
    pass


def fetch_tourresort_page(page_index: int = 1, page_size: int = 100) -> dict[str, Any]:
    if not TOURRESORT_API_KEY:
        raise TourResortApiError("TOURRESORT_API_KEY가 설정되지 않았습니다.")

    params = {
        "KEY": TOURRESORT_API_KEY,
        "Type": "json",
        "pIndex": page_index,
        "pSize": page_size,
    }
    try:
        response = requests.get(TOURRESORT_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.exception("경기도 관광지 API 호출 실패")
        raise TourResortApiError(f"경기도 관광지 API 호출 실패: {exc}") from exc


def extract_tourresort_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    root = payload.get("TouristResort")
    if not isinstance(root, list) or not root:
        raise TourResortApiError("경기도 관광지 응답 형식이 올바르지 않습니다.")

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
                        raise TourResortApiError(f"경기도 관광지 API 오류: {code} {message}")
        if "row" in block and isinstance(block["row"], list):
            rows.extend(item for item in block["row"] if isinstance(item, dict))

    return rows, total
