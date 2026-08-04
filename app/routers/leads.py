from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import Lead, LeadSource, User
from app.schemas import LeadCreate, LeadUpdate, LeadResponse, LeadSourceResponse
from app.auth import get_current_user, RoleChecker
from app.services.ai import analyze_and_score_lead

router = APIRouter(tags=["Leads Management"])

# Helper dependency to check Designer or Admin roles
is_internal_staff = RoleChecker(["Admin", "Designer"])

@router.get("/lead-sources", response_model=List[LeadSourceResponse])
def get_lead_sources(db: Session = Depends(get_db)):
    return db.query(LeadSource).all()

@router.get("/leads", response_model=List[LeadResponse])
def get_leads(
    current_user: User = Depends(is_internal_staff),
    db: Session = Depends(get_db)
):
    """
    Get all leads in the system, sorted by newest first.
    Only internal staff (Admin and Designers) can view the lead pipeline.
    """
    return db.query(Lead).order_by(Lead.created_at.desc()).all()

@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    """
    Submit a lead from the marketing website or external triggers.
    Auto-scores and classifies with AI service.
    """
    # Fetch source name
    source_name = "Website"
    if lead_in.source_id:
        src = db.query(LeadSource).filter(LeadSource.id == lead_in.source_id).first()
        if src:
            source_name = src.name

    # Apply AI Scoring Heuristics
    ai_results = analyze_and_score_lead(
        requirement=lead_in.requirement,
        budget=lead_in.budget,
        source=source_name
    )

    lead = Lead(
        name=lead_in.name,
        phone=lead_in.phone,
        email=lead_in.email,
        source_id=lead_in.source_id,
        budget=lead_in.budget,
        requirement=lead_in.requirement,
        status=lead_in.status or "New",
        ai_score=ai_results["score"],
        ai_classification=ai_results["classification"],
        ai_insights=ai_results["insights"]
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead_by_id(
    lead_id: int,
    current_user: User = Depends(is_internal_staff),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    current_user: User = Depends(is_internal_staff),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_update.model_dump(exclude_unset=True)

    # Re-evaluate AI score if budget or requirement changes
    if "budget" in update_data or "requirement" in update_data:
        req = update_data.get("requirement", lead.requirement)
        bud = update_data.get("budget", lead.budget)
        source_id = update_data.get("source_id", lead.source_id)
        
        source_name = "Website"
        if source_id:
            src = db.query(LeadSource).filter(LeadSource.id == source_id).first()
            if src:
                source_name = src.name
                
        ai_results = analyze_and_score_lead(requirement=req, budget=bud, source=source_name)
        update_data["ai_score"] = ai_results["score"]
        update_data["ai_classification"] = ai_results["classification"]
        update_data["ai_insights"] = ai_results["insights"]

    for key, value in update_data.items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)
    return lead

@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    current_user: User = Depends(RoleChecker(["Admin"])),
    db: Session = Depends(get_db)
):
    """
    Delete a lead by its ID. Only Admin role can perform this.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    return None
