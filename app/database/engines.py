#import sqlalchemy tools for database connections
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

#import application settings
from app.config import settings

def build_database_url(username:str,password:str)->URL:
    """
        build a postgresql database url from shared settings
    """

    return URL.create(
        drivername="postgresql+psycopg2",
        username=username,
        password=password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name
    )

#read only database connection
READONLY_DATABASE_URL=build_database_url(
    settings.db_user,
    settings.db_password
)

readonly_engine=create_engine(
    READONLY_DATABASE_URL,
    pool_pre_ping=True
)

#application database connection
#used for conversations and messages
APP_DATABASE_URL=build_database_url(
    settings.app_db_user,
    settings.app_db_password
)

app_engine=create_engine(
    APP_DATABASE_URL,
    pool_pre_ping=True
)

#etl database connection
#used for data ingestion and transformation pipelines
INGEST_DATABASE_URL=build_database_url(
    settings.ingest_db_user,
    settings.ingest_db_password
)

ingest_engine=create_engine(
    INGEST_DATABASE_URL,
    pool_pre_ping=True
)