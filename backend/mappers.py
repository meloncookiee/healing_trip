from __future__ import annotations

import hashlib
from typing import Any

from models import Attraction, Concert, Temple
from temple_enrichment import build_enrichment


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _float(value: Any) -> float | None:
    text = _text(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def map_templestay_row(row: dict[str, Any]) -> dict[str, Any]:
    name = _text(row.get("INVSTGTN_NM")) or "이름 없음"
    region = _text(row.get("SIGUN_NM"))
    road = _text(row.get("REFINE_ROADNM_ADDR"))
    lot = _text(row.get("REFINE_LOTNO_ADDR"))
    address = road or lot
    phone = _text(row.get("INVSTGTN_TELNO"))
    program = _text(row.get("PROG_TYPE"))
    mountain = _text(row.get("MNTN_NM"))
    zip_code = _text(row.get("REFINE_ZIP_CD"))
    lat = _float(row.get("REFINE_WGS84_LAT"))
    lng = _float(row.get("REFINE_WGS84_LOGT"))

    key_src = "|".join(
        [
            name,
            region or "",
            address or "",
            phone or "",
            _text(row.get("SIGUN_CD")) or "",
        ]
    )
    external_key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()

    description_parts = []
    if mountain and mountain not in ("-", "없음"):
        description_parts.append(
            f"{name}은(는) {mountain} 자락에 위치한 경기도 템플스테이 사찰입니다."
        )
    elif region:
        description_parts.append(
            f"{name}은(는) {region}에 위치한 경기도 템플스테이 사찰입니다."
        )
    else:
        description_parts.append(f"{name} 템플스테이 안내입니다.")

    enrichment = build_enrichment(
        name,
        region=region,
        mountain=mountain,
        program=program,
        phone=phone,
        address=address,
    )

    return {
        "external_key": external_key,
        "name": name,
        "address": address,
        "phone": phone,
        "description": " ".join(description_parts),
        "program": program,
        "homepage": enrichment["homepage"],
        "mountain": mountain,
        "region": region,
        "zip_code": zip_code,
        "lat": lat,
        "lng": lng,
        "image_url": enrichment["image_url"],
        "food": enrichment["food"],
        "environment": enrichment["environment"],
        "specialty": enrichment["specialty"],
        "strengths": enrichment["strengths"],
        "program_intro": enrichment["program_intro"],
        "youtube_url": enrichment.get("youtube_url"),
        "instagram_url": enrichment.get("instagram_url"),
        "intro_text": enrichment.get("intro_text"),
        "guide_text": enrichment.get("guide_text"),
        "facility_text": enrichment.get("facility_text"),
        "gallery_json": enrichment.get("gallery_json"),
        "reviews_json": enrichment.get("reviews_json"),
        "programs_json": enrichment.get("programs_json"),
        "available_dates_json": enrichment.get("available_dates_json"),
        "reservable": enrichment.get("reservable") or 0,
    }


def apply_temple_fields(temple: Temple, data: dict[str, Any]) -> None:
    for key, value in data.items():
        setattr(temple, key, value)


def map_tourguide_row(row: dict[str, Any]) -> dict[str, Any]:
    name = _text(row.get("제목")) or "제목 없음"
    sido = _text(row.get("지역(시_도)"))
    sigungu = _text(row.get("지역(시_군_구)"))
    publisher = _text(row.get("제작처"))
    guidebook_url = _text(row.get("가이드북 링크"))

    address_parts = [part for part in (sido, sigungu) if part]
    address = " ".join(address_parts) if address_parts else None
    region = sigungu or sido

    key_src = "|".join(["guidebook", name, sido or "", sigungu or "", guidebook_url or ""])
    external_key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()

    return {
        "external_key": external_key,
        "name": name,
        "address": address,
        "description": publisher,
        "image_url": None,
        "category": "가이드북",
        "guidebook_url": guidebook_url,
        "sido": sido,
        "sigungu": sigungu,
        "region": region,
        "lat": None,
        "lng": None,
    }


def map_tourresort_row(row: dict[str, Any]) -> dict[str, Any]:
    name = _text(row.get("TOURESRT_NM")) or "이름 없음"
    region = _text(row.get("SIGUN_NM"))
    category = _text(row.get("TOURESRT_DIV_NM")) or "관광지"
    road = _text(row.get("REFINE_ROADNM_ADDR"))
    lot = _text(row.get("REFINE_LOTNO_ADDR"))
    address = road or lot
    operator = _text(row.get("OPERT_MAINBD_NM"))
    area = row.get("APPONT_AR")
    appointed = _text(row.get("APPONT_DE"))
    lat = _float(row.get("REFINE_WGS84_LAT"))
    lng = _float(row.get("REFINE_WGS84_LOGT"))

    desc_parts = []
    if operator:
        desc_parts.append(f"운영: {operator}")
    if area is not None:
        try:
            desc_parts.append(f"지정면적: {float(area):,.0f}㎡")
        except (TypeError, ValueError):
            pass
    if appointed:
        desc_parts.append(f"지정일: {appointed}")

    key_src = "|".join(
        [
            "tourresort",
            name,
            region or "",
            address or "",
            _text(row.get("SIGUN_CD")) or "",
            category,
        ]
    )
    external_key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()

    return {
        "external_key": external_key,
        "name": name,
        "address": address,
        "description": " · ".join(desc_parts) if desc_parts else None,
        "image_url": None,
        "category": category,
        "guidebook_url": None,
        "sido": "경기도",
        "sigungu": region,
        "region": region,
        "lat": lat,
        "lng": lng,
    }


def map_concert_row(row: dict[str, Any]) -> dict[str, Any]:
    title = _text(row.get("TITLE")) or "제목 없음"
    institution = _text(row.get("INST_NM"))
    event_kind = _text(row.get("EVENT_KIND_NM"))
    category = _text(row.get("CLASS_NM"))
    summary = _text(row.get("SUMMRY_SNTNC_CONT"))
    image_url = _text(row.get("IMAGE_URL"))
    period = _text(row.get("EVENT_PERD"))
    place = _text(row.get("EVENT_PLC"))
    detail_url = _text(row.get("SNTNC_URL"))
    registered_at = _text(row.get("SNTNC_REGIST_DE"))

    key_src = "|".join(
        [
            "concert",
            title,
            institution or "",
            period or "",
            place or "",
            detail_url or "",
            registered_at or "",
        ]
    )
    external_key = hashlib.sha1(key_src.encode("utf-8")).hexdigest()

    return {
        "external_key": external_key,
        "title": title,
        "institution": institution,
        "event_kind": event_kind,
        "category": category,
        "summary": summary,
        "image_url": image_url,
        "period": period,
        "place": place,
        "detail_url": detail_url,
        "registered_at": registered_at,
    }


def apply_attraction_fields(attraction: Attraction, data: dict[str, Any]) -> None:
    for key, value in data.items():
        setattr(attraction, key, value)


def apply_concert_fields(concert: Concert, data: dict[str, Any]) -> None:
    for key, value in data.items():
        setattr(concert, key, value)
