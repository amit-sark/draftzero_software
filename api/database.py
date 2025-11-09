from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root@localhost/draftzero_db"


# Engine: put pool_pre_ping here if needed
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

# SessionLocal: only session-related args here
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
