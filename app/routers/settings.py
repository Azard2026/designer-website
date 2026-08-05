from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import os
import shutil
from datetime import datetime

from app.db.database import get_db
from app.models import Setting, User
from app.auth import RoleChecker
from app.schemas import SettingsBulkUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

@router.get("", response_model=Dict[str, str])
def get_all_settings(db: Session = Depends(get_db)):
    """Fetch all site settings (key-value pairs)"""
    settings = db.query(Setting).all()
    return {s.key: s.value for s in settings}

@router.post("/upload")
def upload_image_setting(
    key: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image and set its URL to a setting key"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Create safe unique filename
    ext = file.filename.split(".")[-1]
    safe_filename = f"{key}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    file_url = f"/uploads/{safe_filename}"

    # Update or insert setting
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = file_url
    else:
        setting = Setting(key=key, value=file_url)
        db.add(setting)

    db.commit()
    db.refresh(setting)

    return {"key": setting.key, "value": setting.value, "message": "Image uploaded successfully"}

@router.put("/bulk")
def update_bulk_settings(
    settings_in: SettingsBulkUpdate,
    current_user: User = Depends(RoleChecker(["Admin", "Designer"])),
    db: Session = Depends(get_db)
):
    """Bulk update text settings"""
    for key, value in settings_in.settings.items():
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = Setting(key=key, value=str(value))
            db.add(setting)
    db.commit()
    return {"status": "success", "message": "Settings updated successfully"}
