from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from urllib.parse import quote

# 공공 템플스테이 API에 없는 사진·체험·SNS·안내 정보를
# 사찰명·산·프로그램·지역을 바탕으로 보강한 프로필입니다.

from temple_images import TEMPLE_PHOTO_POOL, place_image_for

DEFAULT_IMAGE = (
    "https://images.unsplash.com/photo-1528164344705-47542687000d?auto=format&fit=crop&w=1200&q=80"
)

# 공식 템플스테이 포털의 사찰별 소개/예약 바로가기
TEMPLE_HOMEPAGES: dict[str, str] = {
    "백련사": "https://baekryunsa.templestay.com/",
    "대원사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%8C%80%EC%9B%90%EC%82%AC",
    "중흥사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%A4%91%ED%9D%A5%EC%82%AC",
    "흥국사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%ED%9D%A5%EA%B5%AD%EC%82%AC+%EA%B3%A0%EC%96%91",
    "연주암": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%97%B0%EC%A3%BC%EC%95%94",
    "금강정사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EA%B8%88%EA%B0%95%EC%A0%95%EC%82%AC",
    "묘적사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%AC%98%EC%A0%81%EC%82%AC",
    "봉선사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%B4%89%EC%84%A0%EC%82%AC",
    "봉인사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%B4%89%EC%9D%B8%EC%82%AC",
    "수진사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%88%98%EC%A7%84%EC%82%AC",
    "대광사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%8C%80%EA%B4%91%EC%82%AC",
    "정토사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%A0%95%ED%86%A0%EC%82%AC",
    "봉녕사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%B4%89%EB%85%95%EC%82%AC",
    "수원사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%88%98%EC%9B%90%EC%82%AC",
    "화운사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%ED%99%94%EC%9A%B4%EC%82%AC",
    "법륜사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EB%B2%95%EB%A5%9C%EC%82%AC",
    "육지장사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%9C%A1%EC%A7%80%EC%9E%A5%EC%82%AC",
    "회암사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%ED%9A%8C%EC%95%94%EC%82%AC",
    "용문사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%9A%A9%EB%AC%B8%EC%82%AC+%EC%96%91%ED%8F%89",
    "사나사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%82%AC%EB%82%98%EC%82%AC",
    "용주사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%9A%A9%EC%A3%BC%EC%82%AC",
    "석왕사": "https://www.templestay.com/fe/MI000000000000000062/temple/list.do?searchKeyword=%EC%84%9D%EC%99%95%EC%82%AC",
}

# 사찰별 SNS (없으면 검색 링크로 대체)
TEMPLE_SNS: dict[str, dict[str, str]] = {
    "봉선사": {
        "youtube": "https://www.youtube.com/results?search_query=%EB%B4%89%EC%84%A0%EC%82%AC+%ED%85%9C%ED%94%8C%EC%8A%A4%ED%85%8C%EC%9D%B4",
        "instagram": "https://www.instagram.com/explore/tags/%EB%B4%89%EC%84%A0%EC%82%AC/",
    },
    "용주사": {
        "youtube": "https://www.youtube.com/results?search_query=%EC%9A%A9%EC%A3%BC%EC%82%AC+%ED%85%9C%ED%94%8C%EC%8A%A4%ED%85%8C%EC%9D%B4",
        "instagram": "https://www.instagram.com/explore/tags/%EC%9A%A9%EC%A3%BC%EC%82%AC/",
    },
    "용문사": {
        "youtube": "https://www.youtube.com/results?search_query=%EC%96%91%ED%8F%89+%EC%9A%A9%EB%AC%B8%EC%82%AC+%ED%85%9C%ED%94%8C%EC%8A%A4%ED%85%8C%EC%9D%B4",
        "instagram": "https://www.instagram.com/explore/tags/%EC%9A%A9%EB%AC%B8%EC%82%AC/",
    },
    "흥국사": {
        "youtube": "https://www.youtube.com/results?search_query=%EA%B3%A0%EC%96%91+%ED%9D%A5%EA%B5%AD%EC%82%AC+%ED%85%9C%ED%94%8C%EC%8A%A4%ED%85%8C%EC%9D%B4",
        "instagram": "https://www.instagram.com/explore/tags/%ED%9D%A5%EA%B5%AD%EC%82%AC/",
    },
}

PROGRAM_GUIDE = {
    "당일형": (
        "당일형 - 하루 일정으로 사찰 안내, 예불·명상 등 핵심 체험을 짧게 경험합니다. "
        "시간이 부족한 분이나 첫 방문에 적합합니다."
    ),
    "체험형": (
        "체험형 - 1박 이상 머물며 발우공양, 참선, 염주·연등 만들기 등 "
        "불교 문화를 비교적 깊이 체험합니다."
    ),
    "휴식형": (
        "휴식형 - 자율 휴식이 중심이며, 공양·예불은 선택 참여합니다. "
        "산사에서 충분히 쉬고 싶은 분에게 맞습니다."
    ),
    "단체형": (
        "단체형 - 가족·동아리·기업 등 단체 일정에 맞춰 상담·예약이 가능합니다."
    ),
}

PROGRAM_THUMBS = {
    "당일형": TEMPLE_PHOTO_POOL[2],
    "체험형": TEMPLE_PHOTO_POOL[3],
    "휴식형": TEMPLE_PHOTO_POOL[4],
    "단체형": TEMPLE_PHOTO_POOL[5],
}

TEMPLE_PROFILES: dict[str, dict[str, str]] = {
    "백련사": {
        "image_url": "https://images.unsplash.com/photo-1528164344705-47542687000d?auto=format&fit=crop&w=1200&q=80",
        "food": "채식 위주 사찰 공양. 체험형에서는 발우공양으로 천천히 나누는 식사를 경험할 수 있습니다.",
        "environment": "축령산 자락의 숲길과 맑은 공기가 돋보이는 가평의 한적한 산사입니다.",
        "specialty": "축령산 자연을 배경으로 한 체험·휴식형 프로그램이 중심입니다.",
        "strengths": "서울·경기 북부에서 당일·1박 모두 접근하기 쉽고, 숲속 고요함이 장점입니다.",
    },
    "대원사": {
        "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
        "food": "계절 나물과 곡물 중심의 담백한 사찰 음식을 제공합니다.",
        "environment": "명지산 자락의 계곡·숲이 가까운 가평의 자연형 사찰입니다.",
        "specialty": "명지산 트레킹과 연계하기 좋은 체험·휴식형 템플스테이.",
        "strengths": "산세가 깊어 도심 소음에서 벗어나기 좋고, 자연 체험과 휴식을 함께 즐길 수 있습니다.",
    },
    "중흥사": {
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "food": "당일·체험 프로그램에 맞춘 간단한 사찰 공양과 차 대접을 경험할 수 있습니다.",
        "environment": "북한산 자락, 고양시에서 접근하기 좋은 도심 근접 산사입니다.",
        "specialty": "당일형·체험형·휴식형을 모두 운영해 일정에 맞춰 고르기 쉽습니다.",
        "strengths": "수도권 접근성이 뛰어나고, 북한산 자연을 가까이에서 느낄 수 있습니다.",
    },
    "흥국사": {
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "food": "담백한 채식 공양과 차 한 잔으로 마음을 가라앉히는 식사가 특징입니다.",
        "environment": "노고산 기슭의 고요한 숲과 도량 분위기가 잘 보존된 곳입니다.",
        "specialty": "고양시에서 즐기는 당일·체험·휴식형 템플스테이.",
        "strengths": "교통이 편리하면서도 산사 특유의 차분한 분위기를 유지합니다.",
    },
    "연주암": {
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "food": "당일형 일정에 맞춘 가벼운 차·공양 체험 위주로 운영됩니다.",
        "environment": "관악산 능선 근처, 과천에서 오르는 전망 좋은 암자입니다.",
        "specialty": "관악산 풍광과 함께하는 당일형 템플스테이.",
        "strengths": "등산과 사찰 체험을 하루 일정으로 묶기 좋아 초보 참가자에게 적합합니다.",
    },
    "금강정사": {
        "image_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "food": "채식 공양과 차 명상을 통해 몸과 마음을 가다듬는 식사를 제공합니다.",
        "environment": "구름산 자락, 광명시 생활권에서 가까운 도심형 힐링 사찰입니다.",
        "specialty": "당일·체험·휴식을 고루 갖춘 광명 지역 템플스테이.",
        "strengths": "시내에서 가까워 부담 없이 찾을 수 있고, 짧은 일정에도 충분합니다.",
    },
    "묘적사": {
        "image_url": "https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1200&q=80",
        "food": "제철 나물과 곡물로 차린 사찰 음식을 중심으로 공양이 이뤄집니다.",
        "environment": "백봉산 자락의 남양주 자연 속, 한적한 산사 분위기입니다.",
        "specialty": "백봉산 숲길과 연계한 체험·휴식형 프로그램.",
        "strengths": "서울 동북부·남양주에서 접근이 쉽고 자연 치유 감성이 강합니다.",
    },
    "봉선사": {
        "image_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?auto=format&fit=crop&w=1200&q=80",
        "food": "전통 사찰 음식과 발우공양 체험으로 느린 식사의 의미를 배웁니다.",
        "environment": "운악산 아래 역사 깊은 가람과 넓은 마당, 울창한 숲이 어우러집니다.",
        "specialty": "남양주를 대표하는 전통 사찰에서의 당일·체험·휴식형 템플스테이.",
        "strengths": "역사·문화 해설과 자연 휴식이 함께 있어 가족·커플 여행에 적합합니다.",
    },
    "봉인사": {
        "image_url": "https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1200&q=80",
        "food": "담백한 채식 공양으로 속을 편안하게 하는 식사를 제공합니다.",
        "environment": "천마산 자락의 맑은 공기와 숲길이 인상적인 남양주 사찰입니다.",
        "specialty": "천마산 자연을 배경으로 한 체험·휴식형 프로그램.",
        "strengths": "산세가 부드러워 산책과 명상을 함께 즐기기 좋습니다.",
    },
    "수진사": {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/Beopjusa-Temple-Stay-Korea_799.jpg",
        "food": "계절 재료를 살린 사찰 공양과 차 대접이 이어집니다.",
        "environment": "천마산로 인근, 도심과 자연이 맞닿은 위치의 사찰입니다.",
        "specialty": "당일부터 휴식형까지 다양한 일정 선택이 가능합니다.",
        "strengths": "접근성이 좋고 프로그램 선택지가 넓어 처음 방문에도 부담이 적습니다.",
    },
    "대광사": {
        "image_url": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80",
        "food": "분당 생활권에서 즐기는 담백한 사찰 음식과 차 한 잔의 여유.",
        "environment": "불곡산 자락, 성남 분당에서 가까운 도심 근접 산사입니다.",
        "specialty": "바쁜 일상에 맞춰 당일·체험·휴식을 고를 수 있습니다.",
        "strengths": "교통이 편리하고 짧은 일정으로도 힐링 효과를 느끼기 좋습니다.",
    },
    "정토사": {
        "image_url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=1200&q=80",
        "food": "채식 공양과 차를 통한 마음 챙김 식사가 특징입니다.",
        "environment": "청계산 자락의 숲과 옛골 풍경이 어우러진 성남 사찰입니다.",
        "specialty": "청계산 트레킹과 함께하기 좋은 템플스테이.",
        "strengths": "산행·명상·휴식을 하루 코스로 구성하기 쉽습니다.",
    },
    "봉녕사": {
        "image_url": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=1200&q=80",
        "food": "수원 지역에서 맛보는 계절 나물 중심의 사찰 공양.",
        "environment": "광교산 아래, 수원 시내에서 비교적 가까운 자연 친화적 도량입니다.",
        "specialty": "광교산 산책과 연계한 당일·체험·휴식형 프로그램.",
        "strengths": "수원·광교 생활권 접근이 쉽고 가족 단위 방문에도 적합합니다.",
    },
    "수원사": {
        "image_url": "https://images.unsplash.com/photo-1418065460487-3e41a6c84dc5?auto=format&fit=crop&w=1200&q=80",
        "food": "당일형 일정에 맞춘 차·간단한 공양 체험 위주로 구성됩니다.",
        "environment": "팔달산·수원천 인근, 도심 속에서도 고요함을 느낄 수 있는 위치입니다.",
        "specialty": "수원 화성 관광과 함께하기 좋은 당일형 템플스테이.",
        "strengths": "시내 관광 동선에 넣기 쉽고, 시간이 짧아도 참여하기 편합니다.",
    },
    "화운사": {
        "image_url": "https://images.unsplash.com/photo-1518173946687-a4c8892bbd9f?auto=format&fit=crop&w=1200&q=80",
        "food": "용인 지역 제철 식재료를 살린 담백한 사찰 음식을 제공합니다.",
        "environment": "멱조산 자락의 조용한 숲과 마을이 가까운 용인 사찰입니다.",
        "specialty": "당일·체험·휴식을 아우르는 용인 템플스테이.",
        "strengths": "처인구 자연과 가까워 주말 힐링 코스로 인기가 있습니다.",
    },
    "법륜사": {
        "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80",
        "food": "농촌 풍경과 어울리는 소박한 채식 공양이 인상적입니다.",
        "environment": "문수산·원삼면의 한적한 농촌·산촌 분위기가 돋보입니다.",
        "specialty": "도심에서 떨어진 진정한 휴식형·체험형 템플스테이.",
        "strengths": "번잡함에서 벗어나 깊이 쉬고 싶은 분에게 특히 잘 맞습니다.",
    },
    "육지장사": {
        "image_url": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80",
        "food": "발우공양·채식 공양으로 천천히 나누는 식사의 의미를 배웁니다.",
        "environment": "도리산 자락, 양주의 한적한 산촌에 자리한 고요한 도량입니다.",
        "specialty": "체험·휴식형 중심의 깊은 산사 프로그램.",
        "strengths": "소음이 적어 명상·휴식에 집중하기 좋습니다.",
    },
    "회암사": {
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "food": "역사 유적지 인근에서 즐기는 담백한 사찰 공양과 차 체험.",
        "environment": "천보산과 회암사지 일대의 역사·자연이 공존하는 공간입니다.",
        "specialty": "회암사지의 역사 탐방과 템플스테이를 함께 경험할 수 있습니다.",
        "strengths": "문화유산 학습과 힐링을 동시에 원하는 여행객에게 적합합니다.",
    },
    "용문사": {
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "food": "산중 사찰의 소박한 채식 공양으로 속을 편안하게 합니다.",
        "environment": "용문산의 울창한 숲과 계곡, 은행나무로 유명한 양평의 대표 산사입니다.",
        "specialty": "휴식형 중심 — 자연 속에서 천천히 머무르는 템플스테이.",
        "strengths": "용문산 관광과 연계하기 좋고, 숲 치유·휴양 목적이 분명합니다.",
    },
    "사나사": {
        "image_url": "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?auto=format&fit=crop&w=1200&q=80",
        "food": "용문산 자락에서 맛보는 계절 나물 공양과 차 한 잔.",
        "environment": "용문산 옥천면의 맑은 계곡과 숲길이 가까운 한적한 사찰입니다.",
        "specialty": "당일·체험·휴식을 모두 갖춘 양평 용문산 템플스테이.",
        "strengths": "용문사와 동선이 가까워 양평 1박 코스를 짜기 좋습니다.",
    },
    "용주사": {
        "image_url": "https://images.unsplash.com/photo-1528164344705-47542687000d?auto=format&fit=crop&w=1200&q=80",
        "food": "전통 가람에서 제공하는 사찰 음식과 차 공양 체험.",
        "environment": "화성 용주사의 고즈넉한 경내와 주변 농촌·산 풍경이 어우러집니다.",
        "specialty": "정조와 연결된 역사 깊은 사찰에서의 체험·휴식형 프로그램.",
        "strengths": "역사·문화 스토리가 풍부하고 경기도 남부 접근성이 좋습니다.",
    },
    "석왕사": {
        "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
        "food": "부천 생활권에서 만나는 담백한 채식 공양과 차 대접.",
        "environment": "도심형 사찰로, 일상과 가까운 위치에서 고요함을 찾을 수 있습니다.",
        "specialty": "당일·체험형 중심으로 부담 없이 참여할 수 있는 템플스테이.",
        "strengths": "대중교통 접근이 쉽고, 처음 템플스테이를 시도하기에 적합합니다.",
    },
}

REVIEW_TEMPLATES = [
    ("민지", "조용히 쉬다 왔어요. 공양도 담백하고 공기가 맑아 좋았습니다."),
    ("준호", "처음 템플스테이인데 안내가 친절해서 부담 없이 참여했어요."),
    ("서연", "숲길 산책과 예불이 인상적이었습니다. 재방문 의사 있어요."),
    ("도윤", "도심에서 가까워 당일 일정으로 다녀오기 딱이었습니다."),
    ("하은", "아이와 함께 왔는데 체험 프로그램이 알차서 만족했어요."),
]


def resolve_homepage(name: str, region: str | None = None) -> str:
    if name in TEMPLE_HOMEPAGES:
        return TEMPLE_HOMEPAGES[name]
    keyword = f"{name} {region}" if region else name
    return (
        "https://www.templestay.com/fe/MI000000000000000062/temple/list.do"
        f"?searchKeyword={quote(keyword)}"
    )


def resolve_sns(name: str) -> dict[str, str]:
    known = TEMPLE_SNS.get(name, {})
    q = quote(f"{name} 템플스테이")
    return {
        "youtube_url": known.get("youtube")
        or f"https://www.youtube.com/results?search_query={q}",
        "instagram_url": known.get("instagram")
        or f"https://www.instagram.com/explore/tags/{quote(name)}/",
    }


def build_program_intro(name: str, program: str | None) -> str:
    raw = (program or "").replace("·", ",")
    types = [part.strip() for part in raw.split(",") if part.strip()]
    lines = [f"{name}에서 현재 안내되는 운영 프로그램입니다."]
    if not types:
        lines.append("상세 일정·예약은 사찰 홈페이지 바로가기에서 확인해 주세요.")
        return "\n".join(lines)

    lines.append(f"운영 유형: {', '.join(types)}")
    for item in types:
        guide = PROGRAM_GUIDE.get(item)
        if guide:
            lines.append(guide)
        else:
            lines.append(f"{item} - 해당 유형의 템플스테이 일정을 운영합니다.")
    lines.append("실제 일정·모집 인원·요금은 시기에 따라 달라질 수 있으니 홈페이지에서 확인해 주세요.")
    return "\n".join(lines)


def _program_types(program: str | None) -> list[str]:
    raw = (program or "").replace("·", ",")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _seed(name: str) -> int:
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:8], 16)


def build_available_dates(name: str, *, weeks: int = 10) -> list[str]:
    """사찰별로 다른 주말·평일 예약 가능일을 생성(안내용)."""
    seed = _seed(name)
    today = date.today()
    dates: list[str] = []
    # 다음 주말 위주 + 일부 평일
    for i in range(weeks * 7):
        d = today + timedelta(days=i + 1)
        weekday = d.weekday()  # 0=월
        pick_weekend = weekday >= 5 and ((seed + i) % 3 != 0)
        pick_weekday = weekday in (2, 3) and ((seed + i) % 5 == 0)
        if pick_weekend or pick_weekday:
            dates.append(d.isoformat())
    return dates[:14]


def build_experience_programs(name: str, program: str | None) -> list[dict]:
    types = _program_types(program)
    if not types:
        return []
    dates = build_available_dates(name)
    programs = []
    for idx, ptype in enumerate(types):
        # 예약 가능: 당일/체험/휴식/단체형만
        reservable = ptype in PROGRAM_GUIDE
        if not reservable:
            continue
        # 프로그램별 날짜 일부 슬라이스
        start = (idx * 2) % max(len(dates), 1)
        prog_dates = dates[start : start + 6] or dates[:4]
        thumb = PROGRAM_THUMBS.get(ptype) or TEMPLE_PHOTO_POOL[idx % len(TEMPLE_PHOTO_POOL)]
        programs.append(
            {
                "id": f"{ptype}-{idx}",
                "name": ptype,
                "image_url": thumb,
                "reservable": True,
                "dates": prog_dates,
                "summary": PROGRAM_GUIDE.get(ptype, f"{name} {ptype} 프로그램"),
            }
        )
    return programs


def build_gallery(name: str) -> list[str]:
    base = place_image_for(name)
    seed = _seed(name)
    gallery = [base]
    for i in range(1, 4):
        gallery.append(TEMPLE_PHOTO_POOL[(seed + i) % len(TEMPLE_PHOTO_POOL)])
    # 중복 제거, 순서 유지
    seen: set[str] = set()
    unique = []
    for url in gallery:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def build_reviews(name: str) -> list[dict]:
    seed = _seed(name)
    picks = []
    for i in range(3):
        author, text = REVIEW_TEMPLATES[(seed + i) % len(REVIEW_TEMPLATES)]
        picks.append(
            {
                "author": author,
                "text": f"{name} — {text}",
                "rating": 4 + ((seed + i) % 2),
            }
        )
    return picks


def build_intro(
    name: str,
    *,
    region: str | None,
    mountain: str | None,
    specialty: str | None,
    strengths: str | None,
) -> str:
    bits = [f"{name}은(는) 경기도 템플스테이를 운영하는 사찰입니다."]
    if region:
        bits.append(f"위치는 {region}입니다.")
    if mountain and mountain not in ("-", "없음"):
        bits.append(f"{mountain} 자락의 자연과 함께합니다.")
    if specialty:
        bits.append(specialty)
    if strengths:
        bits.append(f"장점: {strengths}")
    return " ".join(bits)


def build_guide(name: str, *, phone: str | None = None, address: str | None = None) -> str:
    lines = [
        f"【{name} 사찰안내】",
        "방문 전 예약 여부와 복장(단정한 옷차림)을 확인해 주세요.",
        "경내에서는 큰 소리·흡연을 삼가고, 사진 촬영이 제한된 공간이 있을 수 있습니다.",
    ]
    if address:
        lines.append(f"주소: {address}")
    if phone:
        lines.append(f"문의: {phone}")
    lines.append("상세 일정·요금은 홈페이지 또는 전화로 확인해 주세요.")
    return "\n".join(lines)


def build_facility(name: str, program: str | None) -> str:
    lines = [
        f"【{name} 시설안내】",
        "· 공양실: 채식 공양 제공",
        "· 법당: 예불·명상 공간",
        "· 숙소: 프로그램에 따라 공용/개별 배정",
        "· 화장실·세면: 경내 이용 가능",
    ]
    if program and "체험" in program:
        lines.append("· 체험실: 염주·연등 등 만들기 공간")
    if program and "휴식" in program:
        lines.append("· 휴식 공간: 산책로·마당에서 자율 휴식")
    return "\n".join(lines)


def _program_food(program: str | None) -> str:
    text = program or ""
    if "체험" in text:
        return "체험형 일정에서는 발우공양·채식 공양으로 사찰 음식의 의미를 배웁니다. 자극적이지 않은 계절 나물과 곡물 중심입니다."
    if "휴식" in text:
        return "휴식형에서는 담백한 사찰 공양과 차 한 잔으로 속을 편안하게 하는 식사를 제공합니다."
    return "채식 위주의 사찰 공양이 기본이며, 일정에 따라 차 대접이 포함될 수 있습니다."


def _program_specialty(name: str, program: str | None, mountain: str | None) -> str:
    parts = [f"{name}만의 템플스테이"]
    if mountain and mountain not in ("-", "없음"):
        parts.append(f"{mountain} 자연을 배경으로 합니다")
    if program:
        parts.append(f"운영 프로그램: {program}")
    return ". ".join(parts) + "."


def build_enrichment(
    name: str,
    *,
    region: str | None = None,
    mountain: str | None = None,
    program: str | None = None,
    phone: str | None = None,
    address: str | None = None,
) -> dict:
    profile = dict(TEMPLE_PROFILES.get(name, {}))
    mtn = mountain if mountain and mountain not in ("-", "없음") else None

    profile["homepage"] = resolve_homepage(name, region)
    profile["program_intro"] = build_program_intro(name, program)
    sns = resolve_sns(name)
    profile.update(sns)

    place_img = place_image_for(name)
    profile["image_url"] = place_img or profile.get("image_url") or DEFAULT_IMAGE
    if not profile.get("food"):
        profile["food"] = _program_food(program)
    if not profile.get("environment"):
        if mtn and region:
            profile["environment"] = (
                f"{region} {mtn} 자락에 자리해 숲·산 공기가 맑고, "
                "도량 주변이 비교적 한적한 편입니다."
            )
        elif region:
            profile["environment"] = (
                f"{region}에 위치한 경기도 사찰로, 일상에서 벗어나 마음을 쉬기 좋은 환경입니다."
            )
        else:
            profile["environment"] = "경기도의 자연·도량 분위기 속에서 고요한 시간을 보낼 수 있습니다."
    if not profile.get("specialty"):
        profile["specialty"] = _program_specialty(name, program, mtn)
    if not profile.get("strengths"):
        bits = []
        if region:
            bits.append(f"{region} 접근")
        if program:
            bits.append(f"{program} 운영")
        if mtn:
            bits.append(f"{mtn} 자연 감상")
        profile["strengths"] = (
            " · ".join(bits) if bits else "공공데이터 기반의 신뢰할 수 있는 기본 정보와 힐링 목적의 프로그램"
        )

    programs = build_experience_programs(name, program)
    dates = build_available_dates(name) if programs else []
    profile["intro_text"] = build_intro(
        name,
        region=region,
        mountain=mtn,
        specialty=profile.get("specialty"),
        strengths=profile.get("strengths"),
    )
    profile["guide_text"] = build_guide(name, phone=phone, address=address)
    profile["facility_text"] = build_facility(name, program)
    profile["gallery_json"] = json.dumps(build_gallery(name), ensure_ascii=False)
    profile["reviews_json"] = json.dumps(build_reviews(name), ensure_ascii=False)
    profile["programs_json"] = json.dumps(programs, ensure_ascii=False)
    profile["available_dates_json"] = json.dumps(dates, ensure_ascii=False)
    profile["reservable"] = 1 if programs else 0
    return profile
