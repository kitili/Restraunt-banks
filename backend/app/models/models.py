from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.session import Base

class Nonprofit(Base):
    __tablename__ = "nonprofits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    pickup_windows = relationship("PickupWindow", back_populates="nonprofit", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="nonprofit")

class PickupWindow(Base):
    __tablename__ = "pickup_windows"
    id = Column(Integer, primary_key=True, index=True)
    nonprofit_id = Column(Integer, ForeignKey("nonprofits.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(String, nullable=False)  # "HH:MM" 24h
    end_time = Column(String, nullable=False)

    nonprofit = relationship("Nonprofit", back_populates="pickup_windows")

class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    ready_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    food_description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="posted")  # posted, matched, picked_up, expired

    match = relationship("Match", back_populates="donation", uselist=False)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False, unique=True)
    nonprofit_id = Column(Integer, ForeignKey("nonprofits.id"), nullable=False)
    distance_km = Column(Float, nullable=False)
    pickup_eta = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    donation = relationship("Donation", back_populates="match")
    nonprofit = relationship("Nonprofit", back_populates="matches")
