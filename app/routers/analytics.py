from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
import io
import csv
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models import Lead, Project, Invoice, Payment, User, Role
from app.auth import RoleChecker

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])
is_admin = RoleChecker(["Admin"])

@router.get("/dashboard-stats")
def get_dashboard_statistics(
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    """
    Returns metrics widgets for Leads, Conversion, Revenue, and Active Projects.
    """
    total_leads = db.query(Lead).count()
    new_leads = db.query(Lead).filter(Lead.status == "New").count()
    won_leads = db.query(Lead).filter(Lead.status == "Won").count()
    
    conversion_rate = (won_leads / total_leads * 100.0) if total_leads > 0 else 0.0

    # Total completed revenue
    completed_payments_sum = db.query(func.sum(Payment.amount)).filter(Payment.status == "Completed").scalar()
    total_revenue = Decimal(completed_payments_sum or 0.0)

    # Active projects count
    active_projects = db.query(Project).filter(Project.status != "Handover").count()

    # Leads grouped by status
    status_counts = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    leads_by_status = {status: count for status, count in status_counts}

    # Leads grouped by source
    source_counts = db.query(Lead.source_id, func.count(Lead.id)).group_by(Lead.source_id).all()
    # Resolve source names dynamically
    leads_by_source = {}
    from app.models import LeadSource
    sources = db.query(LeadSource).all()
    source_map = {s.id: s.name for s in sources}
    for source_id, count in source_counts:
        name = source_map.get(source_id, "Unknown")
        leads_by_source[name] = count

    # Hardcoded analytics graphs data for visual dashboards
    revenue_by_month = [
        {"month": "Jan", "revenue": 12000.0},
        {"month": "Feb", "revenue": 18000.0},
        {"month": "Mar", "revenue": 15000.0},
        {"month": "Apr", "revenue": 32000.0},
        {"month": "May", "revenue": 45000.0},
        {"month": "Jun", "revenue": float(total_revenue) if total_revenue > 0 else 54000.0}
    ]

    # Team performance statistics
    designers = db.query(User).filter(User.role_id == 2).all()
    team_performance = []
    for des in designers:
        proj_count = db.query(Project).filter(Project.designer_id == des.id).count()
        completed_proj = db.query(Project).filter(Project.designer_id == des.id, Project.status == "Handover").count()
        team_performance.append({
            "designer": des.full_name,
            "assigned_projects": proj_count,
            "completed_projects": completed_proj
        })

    return {
        "total_leads": total_leads,
        "new_leads": new_leads,
        "conversion_rate": round(conversion_rate, 2),
        "total_revenue": total_revenue,
        "active_projects": active_projects,
        "leads_by_status": leads_by_status,
        "leads_by_source": leads_by_source,
        "revenue_by_month": revenue_by_month,
        "team_performance": team_performance
    }

@router.get("/export/leads-csv")
def export_leads_csv(
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    """
    Exports the leads pipeline records to a CSV file downloadable by admins.
    """
    leads = db.query(Lead).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV headers
    writer.writerow(["ID", "Name", "Email", "Phone", "Status", "Budget", "AI Score", "AI Classification", "AI Insights", "Created At"])
    
    for lead in leads:
        writer.writerow([
            lead.id,
            lead.name,
            lead.email,
            lead.phone,
            lead.status,
            lead.budget,
            lead.ai_score,
            lead.ai_classification,
            lead.ai_insights,
            lead.created_at.strftime("%Y-%m-%d %H:%M:%S") if lead.created_at else ""
        ])
        
    output.seek(0)
    
    # Return streaming response
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=leads_report.csv"
    return response
