# Import SQLAlchemy tools for database connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import application settings
from app.config import settings


# Create the PostgreSQL connection URL
DATABASE_URL = (
    f"postgresql://"
    f"{settings.db_user}:"
    f"{settings.db_password}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}"
)


# Create the SQLAlchemy engine
# The engine manages connections to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# Create a session factory for database operations
# We will use this session when we query or change data
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

#create a databese session for api request
def get_db():
    db=SessionLocal()

    try:
    #give the database session to the api
        yield db

    finally:
        #close the session after the request
        db.close()