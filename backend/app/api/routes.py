from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.models import Nonprofit, PickupWindow, Donation, Match
from ..schemas.schemas import NonprofitCreate, NonprofitOut, DonationCreate, DonationOut, DonationStatusOut, MatchOut
from ..core.matching import find_best_nonprofit

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/nonprofits", response_model=NonprofitOut)
def register_nonprofit(payload: NonprofitCreate, db: Session = Depends(get_db)):
    nonprofit = Nonprofit(
        name=payload.name,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
        active=True,
    )
    db.add(nonprofit)
    db.flush()

    for w in payload.pickup_windows:
        db.add(PickupWindow(nonprofit_id=nonprofit.id, start_time=w.start_time, end_time=w.end_time))

    db.commit()
    db.refresh(nonprofit)
    return nonprofit


@router.post("/donations", response_model=DonationStatusOut)
def post_donation(payload: DonationCreate, db: Session = Depends(get_db)):
    if payload.ready_at >= payload.expires_at:
        raise HTTPException(status_code=400, detail="ready_at must be before expires_at")

    donation = Donation(
        donor_name=payload.donor_name,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        ready_at=payload.ready_at,
        expires_at=payload.expires_at,
        food_description=payload.food_description,
        status="posted",
    )
    db.add(donation)
    db.flush()

    best = find_best_nonprofit(db, donation)
    match_out = None

    if best:
        nonprofit, distance_km, eta = best
        match = Match(
            donation_id=donation.id,
            nonprofit_id=nonprofit.id,
            distance_km=distance_km,
            pickup_eta=eta,
        )
        donation.status = "matched"
        db.add(match)
        db.commit()
        db.refresh(donation)
        match_out = MatchOut(
            match_id=match.id,
            donation_id=match.donation_id,
            nonprofit_id=match.nonprofit_id,
            distance_km=match.distance_km,
            pickup_eta=match.pickup_eta,
        )
    else:
        db.commit()

    return DonationStatusOut(
        donation=DonationOut.model_validate(donation),
        match=match_out,
    )


@router.get("/donations/{donation_id}", response_model=DonationStatusOut)
def get_donation_status(donation_id: int, db: Session = Depends(get_db)):
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    match = db.query(Match).filter(Match.donation_id == donation.id).first()
    match_out = None
    if match:
        match_out = MatchOut(
            match_id=match.id,
            donation_id=match.donation_id,
            nonprofit_id=match.nonprofit_id,
            distance_km=match.distance_km,
            pickup_eta=match.pickup_eta,
        )
    return DonationStatusOut(donation=DonationOut.model_validate(donation), match=match_out)
