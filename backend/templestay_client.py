import logging
from typing import Any

import requests

from config import TEMPLESTAY_API_KEY, TEMPLESTAY_BASE_URL

logger = logging.getLogger(__name__)


class TemplestayApiError(Exception):
    pass


def fetch_templestay_page(page_index: int = 1, page_size: int = 100) -> dict[str, Any]:
    if not TEMPLESTAY_API_KEY:
        raise TemplestayApiError("TEMPLESTAY_API_KEY가 설정되지 않았습니다.")

    params = {
        "KEY": TEMPLESTAY_API_KEY,
        "Type": "json",
        "pIndex": page_index,
        "pSize": page_size,
    }
    try:
        response = requests.get(TEMPLESTAY_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.exception("템플스테이 API 호출 실패")
        raise TemplestayApiError(f"템플스테이 API 호출 실패: {exc}") from exc


def extract_templestay_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    """경기도 OpenAPI JSON 응답에서 row 목록과 총건수를 추출한다."""
    root = payload.get("Templestay")
    if not isinstance(root, list) or not root:
        raise TemplestayApiError("템플스테이 응답 형식이 올바르지 않습니다.")

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
                        raise TemplestayApiError(f"템플스테이 API 오류: {code} {message}")
        if "row" in block and isinstance(block["row"], list):
            rows.extend(item for item in block["row"] if isinstance(item, dict))

    return rows, total
