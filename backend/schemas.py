from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator


class ExperienceProgramOut(BaseModel):
    id: str
    name: str
    image_url: str | None = None
    reservable: bool = True
    dates: list[str] = []
    summary: str | None = None


class TempleReviewOut(BaseModel):
    author: str
    text: str
    rating: int | None = None


def _parse_json_list(value: Any) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            data = json.loads(value)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
    return []


class TempleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str | None = None
    phone: str | None = None
    description: str | None = None
    program: str | None = None
    homepage: str | None = None
    mountain: str | None = None
    region: str | None = None
    zip_code: str | None = None
    lat: float | None = None
    lng: float | None = None
    image_url: str | None = None
    food: str | None = None
    environment: str | None = None
    specialty: str | None = None
    strengths: str | None = None
    program_intro: str | None = None
    youtube_url: str | None = None
    instagram_url: str | None = None
    intro_text: str | None = None
    guide_text: str | None = None
    facility_text: str | None = None
    gallery: list[str] = []
    reviews: list[TempleReviewOut] = []
    experience_programs: list[ExperienceProgramOut] = []
    available_dates: list[str] = []
    reservable: bool = False

    @field_validator("gallery", mode="before")
    @classmethod
    def _gallery(cls, value: Any, info) -> list:
        # from ORM: gallery_json
        return _parse_json_list(value)

    @field_validator("reviews", mode="before")
    @classmethod
    def _reviews(cls, value: Any) -> list:
        return _parse_json_list(value)

    @field_validator("experience_programs", mode="before")
    @classmethod
    def _programs(cls, value: Any) -> list:
        return _parse_json_list(value)

    @field_validator("available_dates", mode="before")
    @classmethod
    def _dates(cls, value: Any) -> list:
        return _parse_json_list(value)

    @field_validator("reservable", mode="before")
    @classmethod
    def _reservable(cls, value: Any) -> bool:
        if value is None:
            return False
        return bool(int(value)) if not isinstance(value, bool) else value


class AttractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str | None = None
    description: str | None = None
    image_url: str | None = None
    category: str | None = None
    guidebook_url: str | None = None
    sido: str | None = None
    sigungu: str | None = None
    region: str | None = None
    lat: float | None = None
    lng: float | None = None
    distance_km: float | None = None


class TempleListResponse(BaseModel):
    items: list[TempleOut]
    total: int


class AttractionListResponse(BaseModel):
    items: list[AttractionOut]
    total: int


class SearchHit(BaseModel):
    type: Literal["temple", "attraction", "concert"]
    id: int
    name: str
    address: str | None = None
    region: str | None = None
    category: str | None = None


class SearchResponse(BaseModel):
    items: list[SearchHit]
    total: int


class ConcertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    institution: str | None = None
    event_kind: str | None = None
    category: str | None = None
    summary: str | None = None
    image_url: str | None = None
    period: str | None = None
    place: str | None = None
    detail_url: str | None = None
    registered_at: str | None = None
    lat: float | None = None
    lng: float | None = None


class ConcertListResponse(BaseModel):
    items: list[ConcertOut]
    total: int


class SyncResponse(BaseModel):
    saved: int
    total: int
    pages: int
    skipped: int | None = None


class RegionListResponse(BaseModel):
    items: list[str]


def to_temple_out(temple: Any) -> TempleOut:
    """ORM Temple → API 스키마 (JSON 컬럼 파싱 포함)."""
    return TempleOut(
        id=temple.id,
        name=temple.name,
        address=temple.address,
        phone=temple.phone,
        description=temple.description,
        program=temple.program,
        homepage=temple.homepage,
        mountain=temple.mountain,
        region=temple.region,
        zip_code=temple.zip_code,
        lat=temple.lat,
        lng=temple.lng,
        image_url=temple.image_url,
        food=temple.food,
        environment=temple.environment,
        specialty=temple.specialty,
        strengths=temple.strengths,
        program_intro=temple.program_intro,
        youtube_url=getattr(temple, "youtube_url", None),
        instagram_url=getattr(temple, "instagram_url", None),
        intro_text=getattr(temple, "intro_text", None),
        guide_text=getattr(temple, "guide_text", None),
        facility_text=getattr(temple, "facility_text", None),
        gallery=_parse_json_list(getattr(temple, "gallery_json", None)),
        reviews=_parse_json_list(getattr(temple, "reviews_json", None)),
        experience_programs=_parse_json_list(getattr(temple, "programs_json", None)),
        available_dates=_parse_json_list(getattr(temple, "available_dates_json", None)),
        reservable=bool(getattr(temple, "reservable", 0) or 0),
    )


def to_concert_out(concert: Any) -> ConcertOut:
    from place_enrichment import concert_image_for, coords_from_place

    lat, lng = coords_from_place(concert.place, concert.institution, concert.title)
    return ConcertOut(
        id=concert.id,
        title=concert.title,
        institution=concert.institution,
        event_kind=concert.event_kind,
        category=concert.category,
        summary=concert.summary,
        image_url=concert_image_for(concert.title, concert.image_url),
        period=concert.period,
        place=concert.place,
        detail_url=concert.detail_url,
        registered_at=concert.registered_at,
        lat=lat,
        lng=lng,
    )


def to_attraction_out(attraction: Any) -> AttractionOut:
    from place_enrichment import attraction_image_for

    image = attraction.image_url or attraction_image_for(
        attraction.name, attraction.category
    )
    return AttractionOut(
        id=attraction.id,
        name=attraction.name,
        address=attraction.address,
        description=attraction.description,
        image_url=image,
        category=attraction.category,
        guidebook_url=attraction.guidebook_url,
        sido=attraction.sido,
        sigungu=attraction.sigungu,
        region=attraction.region,
        lat=attraction.lat,
        lng=attraction.lng,
        distance_km=getattr(attraction, "distance_km", None),
    )
