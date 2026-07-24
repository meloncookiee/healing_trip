from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Attraction, Concert, Temple
from schemas import (
    AttractionListResponse,
    AttractionOut,
    ConcertListResponse,
    ConcertOut,
    RegionListResponse,
    SearchHit,
    SearchResponse,
    SyncResponse,
    TempleListResponse,
    TempleOut,
    to_attraction_out,
    to_concert_out,
    to_temple_out,
)
from store import (
    enrich_temple_if_needed,
    haversine_km,
    sync_attractions,
    sync_concerts,
    sync_temples,
)
from place_enrichment import concert_is_year
from concert_client import ConcertApiError
from templestay_client import TemplestayApiError
from tourguide_client import TourguideApiError
from tourresort_client import TourResortApiError

GYEONGGI_FILTER = or_(
    Attraction.sido.like("%경기%"),
    Attraction.address.like("%경기%"),
    Attraction.region.like("%경기%"),
)

app = FastAPI(title="Healing Trip Gyeonggi API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "healing-trip-gyeonggi"}


@app.post("/temples/sync", response_model=SyncResponse)
def temples_sync(db: Session = Depends(get_db)):
    try:
        result = sync_temples(db)
    except TemplestayApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return result


@app.post("/attractions/sync", response_model=SyncResponse)
def attractions_sync(db: Session = Depends(get_db)):
    try:
        result = sync_attractions(db)
    except (TourguideApiError, TourResortApiError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return result


@app.post("/concerts/sync", response_model=SyncResponse)
def concerts_sync(db: Session = Depends(get_db)):
    try:
        result = sync_concerts(db)
    except ConcertApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return result


@app.get("/temples/regions", response_model=RegionListResponse)
def list_temple_regions(db: Session = Depends(get_db)):
    rows = (
        db.query(Temple.region)
        .filter(Temple.region.isnot(None), Temple.region != "")
        .distinct()
        .order_by(Temple.region.asc())
        .all()
    )
    return {"items": [r[0] for r in rows if r[0]]}


@app.get("/temples", response_model=TempleListResponse)
def list_temples(
    q: str | None = None,
    region: str | None = None,
    date: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Temple)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Temple.name.ilike(like), Temple.address.ilike(like)))
    if region and region.strip():
        query = query.filter(Temple.region == region.strip())

    items = query.order_by(Temple.name.asc()).all()
    changed = False
    for item in items:
        before = (item.programs_json, item.youtube_url)
        enrich_temple_if_needed(item)
        if (item.programs_json, item.youtube_url) != before:
            changed = True
    if changed:
        db.commit()

    if date and date.strip():
        target = date.strip()
        filtered = []
        for item in items:
            out = to_temple_out(item)
            if target in out.available_dates:
                filtered.append(item)
        items = filtered

    total = len(items)
    page = items[offset : offset + limit]
    return {"items": [to_temple_out(item) for item in page], "total": total}


@app.get("/temples/{temple_id}", response_model=TempleOut)
def get_temple(temple_id: int, db: Session = Depends(get_db)):
    temple = db.query(Temple).filter(Temple.id == temple_id).first()
    if temple is None:
        raise HTTPException(status_code=404, detail="템플스테이를 찾을 수 없습니다.")
    enrich_temple_if_needed(temple)
    db.commit()
    db.refresh(temple)
    return to_temple_out(temple)


@app.get("/attractions", response_model=AttractionListResponse)
def list_attractions(
    q: str | None = None,
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Attraction).filter(GYEONGGI_FILTER)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(Attraction.name.ilike(like), Attraction.address.ilike(like))
        )
    if category:
        query = query.filter(Attraction.category == category.strip())
    total = query.count()
    items = query.order_by(Attraction.name.asc()).offset(offset).limit(limit).all()
    return {"items": [to_attraction_out(item) for item in items], "total": total}


@app.get("/attractions/{attraction_id}", response_model=AttractionOut)
def get_attraction(attraction_id: int, db: Session = Depends(get_db)):
    attraction = (
        db.query(Attraction)
        .filter(Attraction.id == attraction_id, GYEONGGI_FILTER)
        .first()
    )
    if attraction is None:
        raise HTTPException(status_code=404, detail="관광지를 찾을 수 없습니다.")
    return to_attraction_out(attraction)


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    like = f"%{q.strip()}%"
    temples = (
        db.query(Temple)
        .filter(or_(Temple.name.ilike(like), Temple.address.ilike(like)))
        .order_by(Temple.name.asc())
        .limit(limit)
        .all()
    )
    remaining = max(limit - len(temples), 0)
    attractions = []
    if remaining > 0:
        attractions = (
            db.query(Attraction)
            .filter(
                GYEONGGI_FILTER,
                or_(Attraction.name.ilike(like), Attraction.address.ilike(like)),
            )
            .order_by(Attraction.name.asc())
            .limit(remaining)
            .all()
        )
    remaining = max(limit - len(temples) - len(attractions), 0)
    concerts = []
    if remaining > 0:
        concerts = (
            db.query(Concert)
            .filter(
                or_(
                    Concert.title.ilike(like),
                    Concert.place.ilike(like),
                    Concert.institution.ilike(like),
                    Concert.summary.ilike(like),
                )
            )
            .order_by(Concert.title.asc())
            .limit(remaining * 3)
            .all()
        )
        concerts = [c for c in concerts if concert_is_year(c, 2026)][:remaining]

    items: list[SearchHit] = [
        SearchHit(
            type="temple",
            id=item.id,
            name=item.name,
            address=item.address,
            region=item.region,
            category=None,
        )
        for item in temples
    ]
    items.extend(
        SearchHit(
            type="attraction",
            id=item.id,
            name=item.name,
            address=item.address,
            region=item.region,
            category=item.category,
        )
        for item in attractions
    )
    items.extend(
        SearchHit(
            type="concert",
            id=item.id,
            name=item.title,
            address=item.place,
            region=item.institution,
            category=item.category or item.event_kind,
        )
        for item in concerts
    )
    return {"items": items, "total": len(items)}


@app.get("/concerts", response_model=ConcertListResponse)
def list_concerts(
    q: str | None = None,
    category: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Concert)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Concert.title.ilike(like),
                Concert.place.ilike(like),
                Concert.institution.ilike(like),
                Concert.summary.ilike(like),
            )
        )
    if category:
        query = query.filter(
            or_(
                Concert.category == category.strip(),
                Concert.event_kind == category.strip(),
            )
        )
    raw = query.order_by(Concert.registered_at.desc(), Concert.title.asc()).all()
    items = [c for c in raw if concert_is_year(c, 2026)]
    total = len(items)
    page = items[offset : offset + limit]
    return {"items": [to_concert_out(item) for item in page], "total": total}


@app.get("/concerts/{concert_id}", response_model=ConcertOut)
def get_concert(concert_id: int, db: Session = Depends(get_db)):
    concert = db.query(Concert).filter(Concert.id == concert_id).first()
    if concert is None:
        raise HTTPException(status_code=404, detail="공연/행사 정보를 찾을 수 없습니다.")
    if not concert_is_year(concert, 2026):
        raise HTTPException(status_code=404, detail="2026년 공연/행사만 제공합니다.")
    return to_concert_out(concert)


@app.get("/temples/{temple_id}/nearby", response_model=AttractionListResponse)
def nearby_attractions(
    temple_id: int,
    radius_km: float = Query(20.0, gt=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    temple = db.query(Temple).filter(Temple.id == temple_id).first()
    if temple is None:
        raise HTTPException(status_code=404, detail="템플스테이를 찾을 수 없습니다.")

    def _normalize_region(value: str | None) -> str:
        text = (value or "").strip()
        for suffix in ("특별자치도", "특별시", "광역시", "자치시", "자치군", "시", "군", "구"):
            if text.endswith(suffix) and len(text) > len(suffix):
                text = text[: -len(suffix)]
                break
        return text

    temple_region = (temple.region or "").strip()
    temple_norm = _normalize_region(temple_region)
    attractions = db.query(Attraction).filter(GYEONGGI_FILTER).all()
    scored: list[tuple[int, AttractionOut]] = []

    for attraction in attractions:
        distance = None
        rank = 99
        if (
            temple.lat is not None
            and temple.lng is not None
            and attraction.lat is not None
            and attraction.lng is not None
        ):
            distance = haversine_km(temple.lat, temple.lng, attraction.lat, attraction.lng)
            if distance > radius_km:
                continue
            rank = 0
        else:
            # 가이드북 데이터는 좌표가 없어 지역명으로 근접 매칭
            region_blob = " ".join(
                filter(
                    None,
                    [attraction.region, attraction.sigungu, attraction.sido, attraction.address],
                )
            )
            attr_norm = " ".join(
                filter(
                    None,
                    [
                        _normalize_region(attraction.region),
                        _normalize_region(attraction.sigungu),
                        _normalize_region(attraction.sido),
                    ],
                )
            )
            if temple_region and temple_region in region_blob:
                rank = 1
            elif temple_norm and temple_norm and temple_norm in attr_norm:
                rank = 2
            elif "경기" in region_blob:
                # 경기도 템플스테이 기준 광역 폴백
                rank = 3
            else:
                continue

        payload = to_attraction_out(attraction)
        payload.distance_km = round(distance, 2) if distance is not None else None
        scored.append((rank, payload))

    scored.sort(
        key=lambda pair: (
            pair[0],
            pair[1].distance_km is None,
            pair[1].distance_km if pair[1].distance_km is not None else 0,
            pair[1].name,
        )
    )
    items = [item for _, item in scored[:limit]]
    return {"items": items, "total": len(scored)}
