# -*- coding: utf-8 -*-
"""공연 연도 판별 · 장소 대략 좌표 · 관광 이미지 보강."""

from __future__ import annotations

import re
from typing import Any

# 경기도 시·군 중심 좌표 (지도 표시용 근사치)
GYEONGGI_COORDS: dict[str, tuple[float, float]] = {
    "가평": (37.8315, 127.5106),
    "고양": (37.6584, 126.8320),
    "과천": (37.4292, 126.9876),
    "광명": (37.4164, 126.8842),
    "광주": (37.4294, 127.2550),
    "구리": (37.5943, 127.1296),
    "군포": (37.3617, 126.9352),
    "김포": (37.6153, 126.7155),
    "남양주": (37.6360, 127.2165),
    "동두천": (37.9034, 127.0606),
    "부천": (37.5034, 126.7660),
    "성남": (37.4449, 127.1389),
    "수원": (37.2636, 127.0286),
    "시흥": (37.3800, 126.8031),
    "안산": (37.3219, 126.8309),
    "안성": (37.0080, 127.2797),
    "안양": (37.3943, 126.9568),
    "양주": (37.7853, 127.0458),
    "양평": (37.4912, 127.4876),
    "여주": (37.2983, 127.6370),
    "연천": (38.0966, 127.0750),
    "오산": (37.1498, 127.0772),
    "용인": (37.2411, 127.1776),
    "의왕": (37.3449, 126.9683),
    "의정부": (37.7381, 127.0338),
    "이천": (37.2720, 127.4350),
    "파주": (37.7599, 126.7800),
    "평택": (36.9921, 127.1129),
    "포천": (37.8949, 127.2002),
    "하남": (37.5393, 127.2149),
    "화성": (37.1995, 126.8313),
    "경기": (37.4138, 127.5183),
}

NATURE_PHOTO_POOL = [
    "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1518173946687-a4c8892bbd9f?auto=format&fit=crop&w=1200&q=80",
]

CONCERT_PHOTO_FALLBACK = [
    "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1511192336575-5a79af67a786?auto=format&fit=crop&w=1200&q=80",
]


def _blob(*parts: Any) -> str:
    return " ".join(str(p) for p in parts if p)


def concert_is_year(data: Any, year: int = 2026) -> bool:
    """2026 탭용: 기간에 2026이 있거나, 종료일 없는 상설(~)만 포함. 과거 종료 일정 제외."""
    if hasattr(data, "period"):
        period = getattr(data, "period", None) or ""
        registered = getattr(data, "registered_at", None) or ""
        title = getattr(data, "title", None) or ""
        summary = getattr(data, "summary", None) or ""
    else:
        period = (data or {}).get("period") or ""
        registered = (data or {}).get("registered_at") or ""
        title = (data or {}).get("title") or ""
        summary = (data or {}).get("summary") or ""

    text = _blob(period, registered, title, summary)
    y = str(year)
    if y in text:
        return True

    p = period.strip()
    open_ended = p in ("", "~") or p.endswith("~") or p.startswith("~")
    years_in_period = [int(x) for x in re.findall(r"20\d{2}", period)]

    # 종료된 과거 일정(닫힌 기간)은 제외
    if years_in_period and not open_ended:
        return min(years_in_period) <= year <= max(years_in_period)

    # 상설·진행중(~) → 2026 탭에 표시
    if open_ended:
        # 기간에 과거 연도만 있고 이미 끝난 것처럼 보이는 "2015-11-07 ~"도
        # 상설로 보고 포함 (공개 API에 2026 데이터가 거의 없음)
        return True

    return False


def coords_from_place(*texts: Any) -> tuple[float | None, float | None]:
    blob = _blob(*texts)
    for name, (lat, lng) in GYEONGGI_COORDS.items():
        if name in blob:
            return lat, lng
    return GYEONGGI_COORDS["경기"]


def attraction_image_for(name: str, category: str | None = None) -> str:
    seed = sum(ord(ch) for ch in f"{name}|{category or ''}")
    return NATURE_PHOTO_POOL[seed % len(NATURE_PHOTO_POOL)]


def concert_image_for(title: str, image_url: str | None = None) -> str:
    if image_url:
        return image_url
    seed = sum(ord(ch) for ch in title or "concert")
    return CONCERT_PHOTO_FALLBACK[seed % len(CONCERT_PHOTO_FALLBACK)]
