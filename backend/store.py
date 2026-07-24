from __future__ import annotations

import logging
import math

from sqlalchemy.orm import Session

from mappers import (
    apply_attraction_fields,
    apply_concert_fields,
    apply_temple_fields,
    map_concert_row,
    map_templestay_row,
    map_tourguide_row,
    map_tourresort_row,
)
from models import Attraction, Concert, Temple
from temple_enrichment import build_enrichment
from templestay_client import (
    TemplestayApiError,
    extract_templestay_rows,
    fetch_templestay_page,
)
from tourguide_client import (
    TourguideApiError,
    extract_tourguide_rows,
    fetch_tourguide_page,
)
from tourresort_client import (
    TourResortApiError,
    extract_tourresort_rows,
    fetch_tourresort_page,
)
from concert_client import (
    ConcertApiError,
    extract_concert_rows,
    fetch_concert_page,
)
from place_enrichment import concert_is_year
logger = logging.getLogger(__name__)


def upsert_temple(db: Session, data: dict) -> Temple:
    temple = db.query(Temple).filter(Temple.external_key == data["external_key"]).first()
    if temple is None:
        temple = Temple(external_key=data["external_key"])
        db.add(temple)
    apply_temple_fields(temple, data)
    return temple


def upsert_attraction(db: Session, data: dict) -> Attraction:
    attraction = (
        db.query(Attraction)
        .filter(Attraction.external_key == data["external_key"])
        .first()
    )
    if attraction is None:
        attraction = Attraction(external_key=data["external_key"])
        db.add(attraction)
    apply_attraction_fields(attraction, data)
    return attraction


def upsert_concert(db: Session, data: dict) -> Concert:
    concert = db.query(Concert).filter(Concert.external_key == data["external_key"]).first()
    if concert is None:
        concert = Concert(external_key=data["external_key"])
        db.add(concert)
    apply_concert_fields(concert, data)
    return concert


def enrich_temple_if_needed(temple: Temple) -> Temple:
    data = build_enrichment(
        temple.name,
        region=temple.region,
        mountain=temple.mountain,
        program=temple.program,
        phone=temple.phone,
        address=temple.address,
    )
    # 공통 포털 대신 사찰별 바로가기 URL 사용
    temple.homepage = data["homepage"]
    temple.program_intro = data["program_intro"]
    # 프로필에 등록된 사진은 항상 최신값으로 맞춤
    temple.image_url = data["image_url"] or temple.image_url
    temple.food = temple.food or data["food"]
    temple.environment = temple.environment or data["environment"]
    temple.specialty = temple.specialty or data["specialty"]
    temple.strengths = temple.strengths or data["strengths"]
    temple.youtube_url = data.get("youtube_url")
    temple.instagram_url = data.get("instagram_url")
    temple.intro_text = data.get("intro_text")
    temple.guide_text = data.get("guide_text")
    temple.facility_text = data.get("facility_text")
    temple.gallery_json = data.get("gallery_json")
    temple.reviews_json = data.get("reviews_json")
    temple.programs_json = data.get("programs_json")
    temple.available_dates_json = data.get("available_dates_json")
    temple.reservable = data.get("reservable") or 0
    if not temple.description or "홈페이지:" in (temple.description or ""):
        mtn = temple.mountain if temple.mountain not in (None, "-", "없음") else None
        if mtn:
            temple.description = (
                f"{temple.name}은(는) {mtn} 자락에 위치한 경기도 템플스테이 사찰입니다."
            )
        elif temple.region:
            temple.description = (
                f"{temple.name}은(는) {temple.region}에 위치한 경기도 템플스테이 사찰입니다."
            )
    return temple


def sync_temples(db: Session, page_size: int = 100) -> dict:
    saved = 0
    page = 1
    total = None

    try:
        while True:
            payload = fetch_templestay_page(page_index=page, page_size=page_size)
            rows, total_count = extract_templestay_rows(payload)
            if total is None:
                total = total_count
            if not rows:
                break

            for row in rows:
                upsert_temple(db, map_templestay_row(row))
                saved += 1
            db.commit()

            if total is not None and page * page_size >= total:
                break
            if len(rows) < page_size:
                break
            page += 1
    except TemplestayApiError:
        db.rollback()
        logger.exception("템플스테이 동기화 실패")
        raise

    return {"saved": saved, "total": total if total is not None else saved, "pages": page}


def _is_gyeonggi(sido: str | None, address: str | None = None) -> bool:
    blob = f"{sido or ''} {address or ''}"
    return "경기" in blob


def sync_attractions(db: Session, per_page: int = 100) -> dict:
    saved = 0
    skipped = 0
    pages = 0

    try:
        # 1) 경기도 관광지(TouristResort)
        page = 1
        resort_total = None
        while True:
            payload = fetch_tourresort_page(page_index=page, page_size=per_page)
            rows, total_count = extract_tourresort_rows(payload)
            if resort_total is None:
                resort_total = total_count
            if not rows:
                break
            for row in rows:
                upsert_attraction(db, map_tourresort_row(row))
                saved += 1
            db.commit()
            pages = max(pages, page)
            if resort_total is not None and page * per_page >= resort_total:
                break
            if len(rows) < per_page:
                break
            page += 1

        # 2) 여행가이드북(경기도만)
        page = 1
        guide_total = None
        while True:
            payload = fetch_tourguide_page(page=page, per_page=per_page)
            rows, total_count = extract_tourguide_rows(payload)
            if guide_total is None:
                guide_total = total_count
            if not rows:
                break
            for row in rows:
                data = map_tourguide_row(row)
                if not _is_gyeonggi(data.get("sido"), data.get("address")):
                    skipped += 1
                    continue
                upsert_attraction(db, data)
                saved += 1
            db.commit()
            pages = max(pages, page)
            if guide_total is not None and page * per_page >= guide_total:
                break
            if len(rows) < per_page:
                break
            page += 1

        extras = (
            db.query(Attraction)
            .filter(~Attraction.sido.like("%경기%"))
            .all()
        )
        for item in extras:
            if not _is_gyeonggi(item.sido, item.address):
                db.delete(item)
        db.commit()
    except (TourResortApiError, TourguideApiError):
        db.rollback()
        logger.exception("관광 정보 동기화 실패")
        raise

    total = saved
    return {
        "saved": saved,
        "total": total,
        "pages": pages or 1,
        "skipped": skipped,
    }


def sync_concerts(db: Session, page_size: int = 100) -> dict:
    """공공 API 동기화 후 2026년(또는 연도 없는 상설)만 남긴다."""
    saved = 0
    skipped = 0
    page = 1
    total = None
    try:
        while True:
            payload = fetch_concert_page(page_index=page, page_size=page_size)
            rows, total_count = extract_concert_rows(payload)
            if total is None:
                total = total_count
            if not rows:
                break
            for row in rows:
                data = map_concert_row(row)
                if not concert_is_year(data, 2026):
                    skipped += 1
                    continue
                upsert_concert(db, data)
                saved += 1
            db.commit()
            if total is not None and page * page_size >= total:
                break
            if len(rows) < page_size:
                break
            page += 1

        # DB에 남아 있는 과거 연도 데이터 정리
        for item in db.query(Concert).all():
            if not concert_is_year(item, 2026):
                db.delete(item)
                skipped += 1
        db.commit()
    except ConcertApiError:
        db.rollback()
        logger.exception("공연 정보 동기화 실패")
        raise
    return {
        "saved": saved,
        "total": total if total is not None else saved,
        "pages": page,
        "skipped": skipped,
    }


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))
