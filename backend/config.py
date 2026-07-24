from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

TEMPLESTAY_API_KEY = os.getenv("TEMPLESTAY_API_KEY", "")
TEMPLESTAY_BASE_URL = os.getenv(
    "TEMPLESTAY_BASE_URL", "https://openapi.gg.go.kr/Templestay"
)

TOURGUIDE_API_KEY = os.getenv("TOURGUIDE_API_KEY", "")
TOURGUIDE_BASE_URL = os.getenv(
    "TOURGUIDE_BASE_URL",
    "https://api.odcloud.kr/api/15123631/v1/uddi:33264f0a-158f-4a5d-95cd-99c740c8a097",
)

TOURRESORT_API_KEY = os.getenv("TOURRESORT_API_KEY", "") or TEMPLESTAY_API_KEY
TOURRESORT_BASE_URL = os.getenv(
    "TOURRESORT_BASE_URL", "https://openapi.gg.go.kr/TouristResort"
)

CONCERT_API_KEY = os.getenv("CONCERT_API_KEY", "") or TEMPLESTAY_API_KEY
CONCERT_BASE_URL = os.getenv(
    "CONCERT_BASE_URL", "https://openapi.gg.go.kr/Ggculturevent"
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
