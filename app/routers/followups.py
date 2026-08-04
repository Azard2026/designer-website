from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Dict, Any

from app.db.database import get_db
from app.models import Followup, Lead, User
from app.schemas import FollowupCreate, FollowupResponse
from app.auth import get_current_user, RoleChecker

router = APIRouter(prefix="/followups", tags=["Follow-up Management"])
is_internal_staff = RoleChecker(["Admin", "Designer"])

@router.get("/dashboard", response_model=Dict[str, Any])
def get_followups_dashboard(
    current_user: User = Depends(is_internal_staff),
    db: Session = Depends(get_db)
):
    """
    Get followups categorized for dashboard widgets:
    - Today's Followups (incomplete, due today)
    - Missed Followups (incomplete, due before today)
    - Upcoming Calls (incomplete, due in future)
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)

    # 1. Today's
    todays = db.query(Followup).filter(
        Followup.is_completed == False,
        Followup.followup_date >= today_start,
        Followup.followup_date <= today_end
    ).order_by(Followup.followup_date.asc()).all()

    # 2. Missed
    missed = db.query(Followup).filter(
        Followup.is_completed == False,
        Followup.followup_date < today_start
    ).order_by(Followup.followup_date.desc()).all()

    # 3. Upcoming
    upcoming = db.query(Followup).filter(
        Followup.is_completed == False,
        Followup.followup_date > today_end
    ).order_by(Followup.followup_date.asc()).all()

    # Helper function to serialize followup with lead info
    def serialize_list(followup_list):
        out = []
        for f in followup_list:
            out.append({
                "id": f.id,
                "lead_id": f.lead_id,
                "lead_name": f.lead.name if f.lead else "Unknown",
                "lead_email": f.lead.email if f.lead else "",
                "lead_phone": f.lead.phone if f.lead else "",
                "followup_date": f.followup_date,
                "followup_type": f.followup_type,
                "notes": f.notes,
                "is_completed": f.is_completed
            })
        return out

    return {
        "todays": serialize_list(todays),
        "missed": serialize_list(missed),
        "upcoming": serialize_list(upcoming)
    }

@router.post("", response_model=FollowupResponse, status_code=status.HTTP_201_CREATED)
def create_followup(
    followup_in: FollowupCreate,
    current_user: User = Depends(is_internal_staff),
    db: Session = Depends(get_db)
):
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == followup_in.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    followup = Followup(
        lead_id=followup_in.lead_id,
        followup_date=followup_in.followup_date,
        followup_type=followup_in.followup_type,
        notes=followup_in.notes,
        is_completed=followup_in.is_completed
    )
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup

@router.patch("/{followup_id}/complete", response_model=FollowupResponse)
def complete_followup(
    followup_id: int,
    current_user: User = Depends(is_internal_staff),
    db: Session = Depends(get_db)
):
    followup = db.query(Followup).filter(Followup.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Followup reminder not found")
        
    followup.is_completed = True
    db.commit()
    db.refresh(followup)
    return followup
