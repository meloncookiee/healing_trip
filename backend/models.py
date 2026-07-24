from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Temple(Base):
    __tablename__ = "temples"

    id = Column(Integer, primary_key=True, index=True)
    external_key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    program = Column(String(255), nullable=True)
    homepage = Column(String(500), nullable=True)
    mountain = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(20), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    image_url = Column(String(1000), nullable=True)
    food = Column(Text, nullable=True)
    environment = Column(Text, nullable=True)
    specialty = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    program_intro = Column(Text, nullable=True)
    youtube_url = Column(String(1000), nullable=True)
    instagram_url = Column(String(1000), nullable=True)
    intro_text = Column(Text, nullable=True)
    guide_text = Column(Text, nullable=True)
    facility_text = Column(Text, nullable=True)
    gallery_json = Column(Text, nullable=True)
    reviews_json = Column(Text, nullable=True)
    programs_json = Column(Text, nullable=True)
    available_dates_json = Column(Text, nullable=True)
    reservable = Column(Integer, nullable=True, default=0)


class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, index=True)
    external_key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    guidebook_url = Column(String(1000), nullable=True)
    sido = Column(String(100), nullable=True)
    sigungu = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)


class Concert(Base):
    __tablename__ = "concerts"

    id = Column(Integer, primary_key=True, index=True)
    external_key = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    institution = Column(String(255), nullable=True)
    event_kind = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    summary = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    period = Column(String(255), nullable=True)
    place = Column(String(500), nullable=True)
    detail_url = Column(String(1000), nullable=True)
    registered_at = Column(String(40), nullable=True)
