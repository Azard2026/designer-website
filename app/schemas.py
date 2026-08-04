from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# JWT and Auth schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role_id: Optional[int] = 3 # Client role default

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Lead & Lead Sources schemas
class LeadBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: EmailStr
    source_id: Optional[int] = None
    budget: Optional[str] = None
    requirement: Optional[str] = None
    status: Optional[str] = "New"

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    source_id: Optional[int] = None
    budget: Optional[str] = None
    requirement: Optional[str] = None
    status: Optional[str] = None
    ai_score: Optional[int] = None
    ai_classification: Optional[str] = None
    ai_insights: Optional[str] = None

class LeadSourceResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class LeadResponse(LeadBase):
    id: int
    ai_score: int
    ai_classification: str
    ai_insights: Optional[str] = None
    source: Optional[LeadSourceResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Followups schemas
class FollowupBase(BaseModel):
    lead_id: int
    followup_date: datetime
    followup_type: str = "Email"
    notes: Optional[str] = None
    is_completed: Optional[bool] = False

class FollowupCreate(FollowupBase):
    pass

class FollowupResponse(FollowupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Tasks schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: str = "Todo"
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    milestone_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Milestones schemas
class MilestoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: str = "Pending"

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    tasks: List[TaskResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Invoice / Payment schemas
class PaymentCreate(BaseModel):
    amount: Decimal
    payment_method: str
    transaction_reference: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: Decimal
    payment_method: str
    transaction_reference: Optional[str] = None
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    invoice_number: str
    amount: Decimal
    due_date: date

class InvoiceResponse(BaseModel):
    id: int
    project_id: int
    invoice_number: str
    amount: Decimal
    due_date: date
    status: str
    payments: List[PaymentResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Documents schemas
class DocumentCreate(BaseModel):
    name: str
    file_url: str
    size: Optional[int] = None
    mime_type: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    project_id: int
    name: str
    file_url: str
    uploaded_by: Optional[int] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "Planning"
    budget: Optional[Decimal] = None
    client_id: Optional[int] = None
    designer_id: Optional[int] = None

class ProjectCreate(ProjectBase):
    lead_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[Decimal] = None
    client_id: Optional[int] = None
    designer_id: Optional[int] = None

class ProjectResponse(ProjectBase):
    id: int
    lead_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = []
    invoices: List[InvoiceResponse] = []
    documents: List[DocumentResponse] = []

    class Config:
        from_attributes = True

# Blog schemas
class BlogCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    category: str
    tags: Optional[str] = None
    status: str = "Draft"

class BlogResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    category: str
    tags: Optional[str] = None
    author_id: Optional[int] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Portfolio schemas
class PortfolioItemResponse(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    description: Optional[str] = None
    before_image_url: Optional[str] = None
    after_image_url: Optional[str] = None
    youtube_url: Optional[str] = None
    budget_range: Optional[str] = None
    client_review: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PortfolioItemCreate(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    before_image_url: Optional[str] = None
    after_image_url: Optional[str] = None
    youtube_url: Optional[str] = None
    budget_range: Optional[str] = None
    client_review: Optional[str] = None

class PortfolioItemUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    before_image_url: Optional[str] = None
    after_image_url: Optional[str] = None
    youtube_url: Optional[str] = None
    budget_range: Optional[str] = None
    client_review: Optional[str] = None

class SettingsBulkUpdate(BaseModel):
    settings: dict


# Testimonial schemas
class TestimonialResponse(BaseModel):
    id: int
    client_name: str
    designation: Optional[str] = None
    content: str
    rating: int
    image_url: Optional[str] = None
    is_featured: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Dashboard Schema
class DashboardStats(BaseModel):
    total_leads: int
    new_leads: int
    conversion_rate: float
    total_revenue: Decimal
    active_projects: int
    leads_by_status: dict
    leads_by_source: dict
    revenue_by_month: list
