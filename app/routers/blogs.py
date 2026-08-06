from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import re
import os
import shutil
import uuid
from datetime import datetime

from app.db.database import get_db
from app.models import Blog, Testimonial, PortfolioItem, User
from app.schemas import BlogCreate, BlogResponse, TestimonialResponse, PortfolioItemResponse, PortfolioItemCreate, PortfolioItemUpdate
from app.auth import get_current_user, RoleChecker
from app.services.ai import generate_blog_content

router = APIRouter(tags=["Public Content & Blogs"])

# Public endpoints (Anonymous accessible)

@router.get("/blogs", response_model=List[BlogResponse])
def get_blogs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Blog).filter(Blog.status == "Published")
    
    if category:
        query = query.filter(Blog.category.ilike(category))
    if search:
        query = query.filter(
            (Blog.title.ilike(f"%{search}%")) | 
            (Blog.summary.ilike(f"%{search}%")) |
            (Blog.content.ilike(f"%{search}%"))
        )
        
    return query.order_by(Blog.created_at.desc()).all()

@router.get("/blogs/{slug}", response_model=BlogResponse)
def get_blog_by_slug(slug: str, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.slug == slug).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog article not found")
    return blog

@router.get("/testimonials", response_model=List[TestimonialResponse])
def get_testimonials(featured_only: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(Testimonial)
    if featured_only:
        query = query.filter(Testimonial.is_featured == True)
    return query.order_by(Testimonial.created_at.desc()).all()

@router.get("/portfolio", response_model=List[PortfolioItemResponse])
def get_portfolio(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PortfolioItem)
    if category:
        query = query.filter(PortfolioItem.category.ilike(category))
    return query.order_by(PortfolioItem.created_at.desc()).all()

@router.get("/portfolio/{slug}", response_model=PortfolioItemResponse)
def get_portfolio_by_slug(slug: str, db: Session = Depends(get_db)):
    item = db.query(PortfolioItem).filter(PortfolioItem.slug == slug).first()
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return item

# Admin/Staff endpoints

@router.post("/blogs", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
def create_blog_post(
    blog_in: BlogCreate,
    run_ai_writer: Optional[bool] = False,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    """
    Create a new blog article. If run_ai_writer is true, it automatically completes the body content and summary using AI content generators.
    """
    title = blog_in.title
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    
    # Check uniqueness
    dup = db.query(Blog).filter(Blog.slug == slug).first()
    if dup:
        # Append identifier to keep it unique
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    content = blog_in.content
    summary = blog_in.summary
    seo_title = f"{title} | Luxe Design"
    seo_description = summary[:140] if summary else ""

    if run_ai_writer:
        ai_data = generate_blog_content(title, blog_in.category)
        content = ai_data["content"]
        summary = ai_data["summary"]
        seo_title = ai_data["seo_title"]
        seo_description = ai_data["seo_description"]

    blog = Blog(
        title=title,
        slug=slug,
        summary=summary,
        content=content,
        category=blog_in.category,
        tags=blog_in.tags,
        author_id=current_user.id,
        seo_title=seo_title,
        seo_description=seo_description,
        status=blog_in.status
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

@router.post("/portfolio", response_model=PortfolioItemResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio_item(
    item_in: PortfolioItemCreate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    # Generate slug from title
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', item_in.title.lower()).strip('-')
    # Check if duplicate slug exists
    dup = db.query(PortfolioItem).filter(PortfolioItem.slug == slug).first()
    if dup:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    item = PortfolioItem(
        title=item_in.title,
        slug=slug,
        category=item_in.category,
        description=item_in.description,
        before_image_url=item_in.before_image_url,
        after_image_url=item_in.after_image_url,
        youtube_url=item_in.youtube_url,
        budget_range=item_in.budget_range,
        client_review=item_in.client_review
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.patch("/portfolio/{item_id}", response_model=PortfolioItemResponse)
def update_portfolio_item(
    item_id: int,
    item_update: PortfolioItemUpdate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    
    # If title is updated, re-generate slug
    if "title" in update_data and update_data["title"] != item.title:
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', update_data["title"].lower()).strip('-')
        dup = db.query(PortfolioItem).filter(PortfolioItem.slug == slug, PortfolioItem.id != item_id).first()
        if dup:
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        update_data["slug"] = slug

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

@router.delete("/portfolio/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_item(
    item_id: int,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    
    db.delete(item)
    db.commit()
    return None

@router.post("/portfolio/upload")
def upload_portfolio_media(
    file: UploadFile = File(...),
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    """Upload portfolio image or video and return URL"""
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # Accept images and videos
    content_type = file.content_type or ""
    if not (content_type.startswith("image/") or content_type.startswith("video/")):
        raise HTTPException(status_code=400, detail="File must be an image or video.")

    ext = (file.filename or "bin").rsplit(".", 1)[-1].lower()
    safe_filename = f"portfolio_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    file_url = f"/uploads/{safe_filename}"
    return {"url": file_url}
