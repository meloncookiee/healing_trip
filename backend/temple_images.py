# -*- coding: utf-8 -*-
"""사찰별 템플스테이 대표 사진. 없으면 템플스테이 갤러리 사진으로 대체."""

from __future__ import annotations

# 템플스테이 갤러리(공식 체험 현장·사찰 사진) — 개별 사진이 없을 때 사용
TEMPLESTAY_GALLERY = [
    "https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_799.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_802.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_818.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_823.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_799.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Heung-guksa_temple_in_Goyang%2C_Korea_01.JPG/1280px-Heung-guksa_temple_in_Goyang%2C_Korea_01.JPG",
    "https://upload.wikimedia.org/wikipedia/commons/c/c3/%EA%B2%BD%EA%B8%B0%EB%8F%84%EB%93%B1%EB%A1%9D%EB%AC%B8%ED%99%94%EC%9E%AC%EC%A0%9C522%ED%98%B8_%EB%82%A8%EC%96%91%EC%A3%BC%EB%B4%89%EC%84%A0%EC%82%AC%ED%81%B0%EB%B2%95%EB%8B%B9_%EB%B4%89%EC%84%A0%EC%82%AC%ED%81%B0%EB%B2%95%EB%8B%B92.jpg",
    "https://commons.wikimedia.org/wiki/Special:FilePath/%ED%99%94%EC%84%B1_%EC%9A%A9%EC%A3%BC%EC%82%AC_%EB%8F%99%EC%A2%85_01.jpg?width=1280",
    "https://upload.wikimedia.org/wikipedia/commons/4/4e/Temple_Silleuk.JPG",
    "https://upload.wikimedia.org/wikipedia/commons/f/fa/Korean_Temple_At_Night_(177102903).jpeg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Bulguksa_Temple-Gyeongju-Korea-2006-10b.jpg/1280px-Bulguksa_Temple-Gyeongju-Korea-2006-10b.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Yeongju_Buseoksa_Temple_01.jpg/1280px-Yeongju_Buseoksa_Temple_01.jpg",
]

# 하위 호환
TEMPLE_PHOTO_POOL = TEMPLESTAY_GALLERY

# 사찰별 전용(또는 동일 사찰·권역) 사진 — 반드시 채움
TEMPLE_PLACE_IMAGES: dict[str, str] = {
    "백련사": TEMPLESTAY_GALLERY[0],
    "대원사": TEMPLESTAY_GALLERY[1],
    "중흥사": TEMPLESTAY_GALLERY[5],
    "흥국사": TEMPLESTAY_GALLERY[5],
    "연주암": TEMPLESTAY_GALLERY[2],
    "금강정사": TEMPLESTAY_GALLERY[3],
    "묘적사": TEMPLESTAY_GALLERY[6],
    "봉선사": TEMPLESTAY_GALLERY[6],
    "봉인사": TEMPLESTAY_GALLERY[4],
    "수진사": TEMPLESTAY_GALLERY[0],
    "대광사": TEMPLESTAY_GALLERY[1],
    "정토사": TEMPLESTAY_GALLERY[2],
    "봉녕사": TEMPLESTAY_GALLERY[3],
    "수원사": TEMPLESTAY_GALLERY[8],
    "화운사": TEMPLESTAY_GALLERY[4],
    "법륜사": TEMPLESTAY_GALLERY[9],
    "육지장사": TEMPLESTAY_GALLERY[10],
    "회암사": TEMPLESTAY_GALLERY[5],
    "용문사": TEMPLESTAY_GALLERY[11],
    "사나사": TEMPLESTAY_GALLERY[1],
    "용주사": TEMPLESTAY_GALLERY[7],
    "석왕사": TEMPLESTAY_GALLERY[2],
}

DEFAULT_TEMPLE_PHOTO = TEMPLESTAY_GALLERY[0]


def place_image_for(name: str) -> str:
    """사찰별 사진. 없으면 템플스테이 갤러리에서 안정적으로 하나 선택."""
    if name in TEMPLE_PLACE_IMAGES:
        return TEMPLE_PLACE_IMAGES[name]
    idx = sum(ord(ch) for ch in (name or "temple")) % len(TEMPLESTAY_GALLERY)
    return TEMPLESTAY_GALLERY[idx]


def gallery_fallback(index: int = 0) -> str:
    return TEMPLESTAY_GALLERY[index % len(TEMPLESTAY_GALLERY)]
