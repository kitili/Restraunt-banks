from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class PickupWindowCreate(BaseModel):
    start_time: str = Field(description="HH:MM 24h")
    end_time: str = Field(description="HH:MM 24h")

class NonprofitCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    pickup_windows: List[PickupWindowCreate]

class NonprofitOut(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

class DonationCreate(BaseModel):
    donor_name: str
    address: str
    latitude: float
    longitude: float
    ready_at: datetime
    expires_at: datetime
    food_description: str

class DonationOut(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True

class MatchOut(BaseModel):
    match_id: int
    donation_id: int
    nonprofit_id: int
    distance_km: float
    pickup_eta: datetime

class DonationStatusOut(BaseModel):
    donation: DonationOut
    match: Optional[MatchOut] = None
