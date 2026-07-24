import logging
from typing import Any

import requests

from config import TOURGUIDE_API_KEY, TOURGUIDE_BASE_URL

logger = logging.getLogger(__name__)


class TourguideApiError(Exception):
    pass


def fetch_tourguide_page(page: int = 1, per_page: int = 100) -> dict[str, Any]:
    if not TOURGUIDE_API_KEY:
        raise TourguideApiError("TOURGUIDE_API_KEY가 설정되지 않았습니다.")

    headers = {"Authorization": f"Infuser {TOURGUIDE_API_KEY}"}
    params = {
        "page": page,
        "perPage": per_page,
        "returnType": "JSON",
    }
    try:
        response = requests.get(
            TOURGUIDE_BASE_URL, headers=headers, params=params, timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.exception("여행가이드북 API 호출 실패")
        raise TourguideApiError(f"여행가이드북 API 호출 실패: {exc}") from exc


def extract_tourguide_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    data = payload.get("data")
    if not isinstance(data, list):
        raise TourguideApiError("여행가이드북 응답 형식이 올바르지 않습니다.")

    total = int(payload.get("totalCount") or payload.get("matchCount") or len(data))
    rows = [item for item in data if isinstance(item, dict)]
    return rows, total
