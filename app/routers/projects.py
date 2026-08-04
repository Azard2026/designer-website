from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models import Project, User, Milestone, Task, Invoice, Payment, Document, Role
from app.schemas import (
    ProjectBase, ProjectCreate, ProjectResponse, ProjectUpdate,
    MilestoneCreate, MilestoneResponse,
    TaskCreate, TaskResponse,
    InvoiceCreate, InvoiceResponse,
    PaymentCreate, PaymentResponse,
    DocumentCreate, DocumentResponse
)
from app.auth import get_current_user, RoleChecker

router = APIRouter(prefix="/projects", tags=["Project Management"])

def check_project_access(project_id: int, user: User, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check roles
    user_role = db.query(Role).filter(Role.id == user.role_id).first()
    role_name = user_role.name if user_role else "Client"
    
    if role_name == "Client" and project.client_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project"
        )
    return project

@router.get("", response_model=List[ProjectResponse])
def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get projects list. Clients see only their projects; staff sees all.
    """
    user_role = db.query(Role).filter(Role.id == current_user.role_id).first()
    role_name = user_role.name if user_role else "Client"
    
    if role_name == "Client":
        return db.query(Project).filter(Project.client_id == current_user.id).all()
    else:
        return db.query(Project).all()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    project = Project(
        lead_id=project_in.lead_id,
        name=project_in.name,
        description=project_in.description,
        status=project_in.status,
        budget=project_in.budget,
        client_id=project_in.client_id,
        designer_id=project_in.designer_id or current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return check_project_access(project_id, current_user, db)

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project

# Milestone Add
@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
def add_milestone(
    project_id: int,
    milestone_in: MilestoneCreate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    milestone = Milestone(
        project_id=project_id,
        name=milestone_in.name,
        description=milestone_in.description,
        due_date=milestone_in.due_date,
        status=milestone_in.status
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone

# Task Add
@router.post("/milestones/{milestone_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def add_task(
    milestone_id: int,
    task_in: TaskCreate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
        
    task = Task(
        milestone_id=milestone_id,
        title=task_in.title,
        description=task_in.description,
        assigned_to=task_in.assigned_to,
        status=task_in.status,
        due_date=task_in.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# Invoice Add
@router.post("/{project_id}/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def add_invoice(
    project_id: int,
    invoice_in: InvoiceCreate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    invoice = Invoice(
        project_id=project_id,
        invoice_number=invoice_in.invoice_number,
        amount=invoice_in.amount,
        due_date=invoice_in.due_date,
        status="Sent"
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

# Submit Invoice Payment
@router.post("/invoices/{invoice_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def submit_payment(
    invoice_id: int,
    payment_in: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Settle payments
    payment = Payment(
        invoice_id=invoice_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        transaction_reference=payment_in.transaction_reference,
        status="Completed", # Autocomplete mock for visual ease
        paid_at=datetime.utcnow()
    )
    db.add(payment)
    
    # Update invoice status
    invoice.status = "Paid"
    
    db.commit()
    db.refresh(payment)
    return payment

# Document Add
@router.post("/{project_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def add_document(
    project_id: int,
    doc_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify access first
    check_project_access(project_id, current_user, db)
    
    document = Document(
        project_id=project_id,
        name=doc_in.name,
        file_url=doc_in.file_url,
        uploaded_by=current_user.id,
        size=doc_in.size,
        mime_type=doc_in.mime_type
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
