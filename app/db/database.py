import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# MySQL is required in production. SQLite remains available only for local
# development when DATABASE_URL is explicitly set to a sqlite URL.
DATABASE_URL = "mysql+pymysql://designer:Password@123@localhost/designer_db"
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        if DATABASE_URL.startswith("sqlite"):
            db.execute(text("PRAGMA foreign_keys = ON"))
        yield db
    finally:
        db.close()


def _seed_initial_data(db):
    """Create the initial, idempotent demo/admin data for an empty database."""
    from app.models import Blog, LeadSource, Permission, PortfolioItem, Role, Setting, Testimonial, User

    if db.query(Role).first():
        return

    roles = [
        Role(id=1, name="Admin", description="Platform administrator with full control"),
        Role(id=2, name="Designer", description="Interior Designer"),
        Role(id=3, name="Client", description="Client portal user"),
    ]
    permissions = [
        Permission(id=1, name="manage_users"), Permission(id=2, name="manage_leads"),
        Permission(id=3, name="manage_projects"), Permission(id=4, name="client_portal_access"),
    ]
    roles[0].permissions = permissions
    roles[1].permissions = permissions[1:]
    roles[2].permissions = [permissions[3]]
    db.add_all(roles + permissions)
    db.flush()

    db.add_all([
        User(id=1, email="admin@kelebekdesigners.com", password_hash="$2b$12$7kP.Lz39/4ZzV5X.fU.LHe.x7k26b1E83.0B7e930/1u/Q0K9Z2lW", full_name="Kelebek Admin", phone="+91 98765 43210", role_id=1),
        User(id=2, email="sarah.designer@kelebekdesigners.com", password_hash="$2b$12$7kP.Lz39/4ZzV5X.fU.LHe.x7k26b1E83.0B7e930/1u/Q0K9Z2lW", full_name="Sarah Jenkins", phone="+91 98765 43211", role_id=2),
        User(id=3, email="robert.client@gmail.com", password_hash="$2b$12$7kP.Lz39/4ZzV5X.fU.LHe.x7k26b1E83.0B7e930/1u/Q0K9Z2lW", full_name="Robert Miller", phone="+91 98765 43212", role_id=3),
    ])
    db.add_all([LeadSource(id=i, name=name) for i, name in enumerate(["Website", "WhatsApp", "Google Ads", "Instagram", "Facebook", "Referral"], 1)])
    db.add_all([
        PortfolioItem(id=1, title="Kelebek Royal Villa Sanctuary", slug="kelebek-royal-villa", category="Residential", description="A complete overhaul of a luxury villa.", before_image_url="/images/hero_interior_1784468037551.png", after_image_url="/images/hero_interior_1784468037551.png", budget_range="₹25 Lakhs – ₹45 Lakhs", client_review="Kelebek Designers turned our house into an architectural masterpiece."),
        PortfolioItem(id=2, title="Solas Corporate Office & Lounge", slug="solas-corporate-office", category="Commercial", description="A premium commercial office layout.", before_image_url="/images/portfolio_commercial_1784468061607.png", after_image_url="/images/portfolio_commercial_1784468061607.png", budget_range="₹35 Lakhs+", client_review="Our team productivity spiked."),
        PortfolioItem(id=3, title="Bespoke Italian Culinary Suite", slug="italian-culinary-suite", category="Modular Kitchen", description="A premium culinary kitchen design.", before_image_url="/images/portfolio_kitchen_1784468083139.png", after_image_url="/images/portfolio_kitchen_1784468083139.png", budget_range="₹8 Lakhs – ₹15 Lakhs", client_review="Absolute perfection."),
    ])
    db.add_all([
        Testimonial(id=1, client_name="Rajesh & Meera Kapoor", designation="Villa Owners, Mumbai", content="Kelebek Designers completely redefined how we live.", rating=5, image_url="/images/hero_interior_1784468037551.png", is_featured=True),
        Testimonial(id=2, client_name="Vikram Malhotra", designation="CEO, InovaTech India", content="They delivered on time and within budget.", rating=5, image_url="/images/portfolio_commercial_1784468061607.png", is_featured=True),
    ])
    db.add(Blog(id=1, title="The Art of Minimalist Luxury: Designing Indian Homes", slug="art-of-minimalist-luxury", summary="A guide to quiet luxury.", content="<h2>Understanding Quiet Luxury</h2><p>Luxury is expressed through deliberate material and layout choices.</p>", category="Residential", tags="Luxury, Minimalist, Guide", author_id=2, seo_title="Luxury Minimalist Interior Design | Kelebek Designers", seo_description="Learn how to apply quiet luxury.", status="Published"))
    db.add_all([Setting(id=i, key=key, value=value) for i, (key, value) in enumerate([
        ("site_name", "KELEBEK DESIGNERS"), ("contact_email", "contact@kelebekdesigners.com"),
        ("contact_phone", "+91 98765 43210"), ("office_address", "KELEBEK DESIGNERS STUDIO, India"),
    ], 1)])
    db.commit()


def init_db():
    # Importing models registers every table with SQLAlchemy metadata.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_initial_data(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
