import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Read from env, fallback to sqlite if no DB url is provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./designer_website.db")

# For SQLite, allow multi-threaded access
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def split_sql_statements(sql_text):
    statements = []
    current = []
    in_string = False
    escape = False
    for char in sql_text:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == '\\':
            current.append(char)
            escape = True
            continue
        if char == "'":
            in_string = not in_string
        current.append(char)
        if char == ';' and not in_string:
            statements.append("".join(current).strip())
            current = []
    if current:
        rest = "".join(current).strip()
        if rest:
            statements.append(rest)
    return statements

def get_db():
    db = SessionLocal()
    try:
        # Enable foreign key support for sqlite
        if DATABASE_URL.startswith("sqlite"):
            db.execute(text("PRAGMA foreign_keys = ON;"))
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database. If running on SQLite, it will automatically load the
    schema.sql and seed.sql to configure the tables and mock database state.
    """
    # Create tables via SQL script if database is fresh
    db = SessionLocal()
    try:
        # Determine check query based on database type (SQLite, MySQL, or PostgreSQL)
        if DATABASE_URL.startswith("sqlite"):
            table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        elif "mysql" in DATABASE_URL:
            table_check_query = "SHOW TABLES LIKE 'users';"
        else:
            table_check_query = "SELECT to_regclass('public.users');"

        result = db.execute(text(table_check_query)).fetchone()
        
        if not result or result[0] is None:
            print("Database is empty. Initializing schema and seed data...")
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
            
            # Read and execute schema
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                # Split queries to execute individually (important for SQLite)
                statements = split_sql_statements(schema_sql)
                for statement in statements:
                    try:
                        # SQLite doesn't support 'DROP TABLE ... CASCADE' natively, we patch it
                        if DATABASE_URL.startswith("sqlite"):
                            if statement.upper().startswith("DROP TABLE"):
                                statement = statement.replace("CASCADE", "")
                            statement = statement.replace("NUMERIC(12, 2)", "REAL").replace("TIMESTAMP WITH TIME ZONE", "TIMESTAMP")
                            # SQLite auto-increments with AUTOINCREMENT, not SERIAL (but PRIMARY KEY is sufficient)
                            statement = statement.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
                            # Remove CHECK constraints with arrays not supported cleanly
                            if "CHECK (status IN" in statement:
                                # Keep simple definition
                                pass
                        db.execute(text(statement))
                    except Exception as e:
                        print(f"Warning during schema run of statement: {statement[:50]}... Error: {e}")
                db.commit()
                print("Schema loaded successfully.")

            # Read and execute seed data
            if os.path.exists(seed_path):
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed_sql = f.read()
                statements = split_sql_statements(seed_sql)
                for statement in statements:
                    try:
                        if DATABASE_URL.startswith("sqlite"):
                            # SQLite patches
                            statement = statement.replace("CURRENT_TIMESTAMP + INTERVAL '1 hour'", "datetime('now', '+1 hour')")
                            statement = statement.replace("CURRENT_TIMESTAMP - INTERVAL '1 day'", "datetime('now', '-1 day')")
                            statement = statement.replace("CURRENT_TIMESTAMP + INTERVAL '2 days'", "datetime('now', '+2 days')")
                            if "SELECT setval" in statement:
                                continue # Skip postgres sequence updater
                        db.execute(text(statement))
                    except Exception as e:
                        print(f"Warning during seeding of statement: {statement[:50]}... Error: {e}")
                db.commit()
                print("Seed data loaded successfully.")
    except Exception as err:
        print(f"Failed to initialize database: {err}")
    finally:
        db.close()

    # --- Safe migration: add new columns if they don't exist yet ---
    migration_db = SessionLocal()
    try:
        migrations = [
            "ALTER TABLE portfolio_items ADD COLUMN youtube_url TEXT",
        ]
        for migration in migrations:
            try:
                migration_db.execute(text(migration))
                migration_db.commit()
                print(f"Migration applied: {migration[:60]}")
            except Exception:
                migration_db.rollback()  # Column already exists — safe to ignore
    finally:
        migration_db.close()

