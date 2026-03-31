from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "sqlite:///./saas.db"
DATABASE_URL = "postgresql://postgres.bwytctyavlypxbueqykr:aaga!2150b552919101@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
